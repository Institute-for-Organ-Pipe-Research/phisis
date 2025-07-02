import os
import tkinter as tk
from tkinter import filedialog, ttk
import numpy as np
from scipy import signal
import soundfile as sf
from threading import Thread
import queue
import librosa

class PipeDenoiser:
    def __init__(self):
        self.sr = 44100
        
    def normalize(self, audio):
        """Normalizacja amplitudy do zakresu [-1, 1]"""
        peak = np.max(np.abs(audio))
        if peak > 0:
            return audio / peak
        return audio
        
    def safe_denoise(self, audio, strength=0.85):
        """
        Usuwanie pogłosu przy użyciu redukcji szumu spektralnego
        z zabezpieczeniem przed artefaktami
        """
        # Konwersja do dziedziny częstotliwości (STFT)
        S = librosa.stft(audio.astype(np.float32))
        magnitude, phase = librosa.magphase(S)
        
        # Oblicz szacowane tło (pogłos)
        background = librosa.decompose.nn_filter(
            magnitude,
            aggregate=np.median,
            metric='cosine',
            width=int(librosa.time_to_frames(0.2, sr=self.sr))
        )
        
        # Maska do usuwania tła
        mask = np.maximum(1.0 - strength * (background / magnitude), 0)
        clean_magnitude = magnitude * mask
        
        # Rekonstrukcja sygnału
        clean_S = clean_magnitude * phase
        clean_audio = librosa.istft(clean_S)
        
        return clean_audio.astype(np.float32)

    def process_note(self, a0_path, r_paths, output_path, strength=0.85, progress_queue=None):
        try:
            # Wczytaj próbkę A0
            a0_audio, sr = sf.read(a0_path)
            if a0_audio.ndim > 1:
                a0_audio = np.mean(a0_audio, axis=1)
            self.sr = sr

            # Normalizuj A0
            a0_audio = self.normalize(a0_audio)

            # Wczytaj i uśrednij próbki R
            r_audios = []
            for r_path in r_paths:
                if os.path.exists(r_path):
                    r_audio, r_sr = sf.read(r_path)
                    if r_audio.ndim > 1:
                        r_audio = np.mean(r_audio, axis=1)
                    if r_sr != sr:
                        r_audio = signal.resample(r_audio, int(len(r_audio) * sr / r_sr))
                    r_audios.append(self.normalize(r_audio))

            # Uśrednij próbki R
            avg_r = np.zeros_like(r_audios[0]) if r_audios else np.array([])
            if r_audios:
                max_len = max(len(r) for r in r_audios)
                avg_r = np.zeros(max_len)
                for r in r_audios:
                    avg_r[:len(r)] += r[:len(r)]
                avg_r /= len(r_audios)
                avg_r = self.normalize(avg_r)

            # Połącz A0 z uśrednionym R
            if len(avg_r) > 0:
                crossfade = min(int(0.5 * sr), len(a0_audio)//3, len(avg_r)//3)
                if crossfade > 0:
                    fade_out = np.linspace(1, 0, crossfade)
                    fade_in = np.linspace(0, 1, crossfade)
                    transition = a0_audio[-crossfade:] * fade_out + avg_r[:crossfade] * fade_in
                    combined = np.concatenate([
                        a0_audio[:-crossfade],
                        transition,
                        avg_r[crossfade:]
                    ])
                else:
                    combined = np.concatenate([a0_audio, avg_r])
            else:
                combined = a0_audio

            # Usuń pogłos z całej próbki
            cleaned = self.safe_denoise(combined, strength)

            # Zapisz wynik
            sf.write(output_path, cleaned, sr)
            if progress_queue:
                progress_queue.put(('success', os.path.basename(output_path)))
            return True

        except Exception as e:
            if progress_queue:
                progress_queue.put(('error', f"{os.path.basename(a0_path)}: {str(e)}"))
            return False


class DenoiserGUI:
    def __init__(self, root):
        self.root = root
        root.title("Organ Pipe Denoiser")
        root.geometry("900x650")
        
        self.denoiser = PipeDenoiser()
        self.progress_queue = queue.Queue()
        
        # Variables
        self.root_dir = tk.StringVar()
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "denoised_output"))
        self.strength = tk.DoubleVar(value=0.85)
        self.status = tk.StringVar(value="Ready")
        self.files = []
        
        # GUI Setup
        self.create_widgets()
        self.check_queue()

    def create_widgets(self):
        # Frame for directory selection
        dir_frame = ttk.Frame(self.root, padding="10")
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Root directory
        ttk.Label(dir_frame, text="Root Directory:").grid(row=0, column=0, sticky=tk.W)
        root_entry = ttk.Entry(dir_frame, textvariable=self.root_dir, width=50)
        root_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Button(dir_frame, text="Browse...", command=self.browse_root).grid(row=0, column=2)
        
        # Output directory
        ttk.Label(dir_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W)
        output_entry = ttk.Entry(dir_frame, textvariable=self.output_dir, width=50)
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))
        ttk.Button(dir_frame, text="Browse...", command=self.browse_output).grid(row=1, column=2)
        
        # Refresh button
        ttk.Button(dir_frame, text="Refresh List", command=self.refresh_list).grid(row=2, column=0, columnspan=3, pady=5)
        
        # Treeview for files
        tree_frame = ttk.Frame(self.root, padding="10")
        tree_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        self.tree = ttk.Treeview(tree_frame, columns=('status'), show='tree headings')
        self.tree.heading('#0', text='Sample')
        self.tree.heading('status', text='R Files')
        self.tree.column('status', width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Processing controls
        ctrl_frame = ttk.Frame(self.root, padding="10")
        ctrl_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(ctrl_frame, text="Denoise Strength:").grid(row=0, column=0)
        strength_slider = ttk.Scale(ctrl_frame, from_=0.1, to=1.0, variable=self.strength)
        strength_slider.grid(row=0, column=1)
        
        self.process_btn = ttk.Button(ctrl_frame, text="Process Selected", command=self.process_selected)
        self.process_btn.grid(row=0, column=4, padx=10)
        
        self.process_all_btn = ttk.Button(ctrl_frame, text="Process All", command=self.process_all)
        self.process_all_btn.grid(row=0, column=5)
        
        # Status bar
        status_frame = ttk.Frame(self.root, padding="10")
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        ttk.Label(status_frame, textvariable=self.status).pack(side=tk.LEFT)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

    def browse_root(self):
        directory = filedialog.askdirectory(title="Select Root Directory")
        if directory:
            self.root_dir.set(directory)
            self.refresh_list()

    def browse_output(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        self.files = []
        
        root_dir = self.root_dir.get()
        if not root_dir or not os.path.exists(root_dir):
            return
            
        a0_dir = os.path.join(root_dir, "A0")
        if not os.path.exists(a0_dir):
            self.status.set("Error: A0 folder not found in root directory")
            return
            
        # Find all note files in A0
        note_files = [f for f in os.listdir(a0_dir) if f.endswith('.wav')]
        
        for note_file in sorted(note_files):
            base_name = os.path.splitext(note_file)[0]  # np. "036-c"
            
            # Find corresponding R files
            r_files = []
            for r_dir in ["R0", "R1", "R2", "R3"]:
                r_path = os.path.join(root_dir, r_dir, note_file)
                if os.path.exists(r_path):
                    r_files.append(r_path)
            
            # Wyświetl pełną nazwę pliku w liście
            item = self.tree.insert('', 'end', text=base_name, 
                                  values=(f"R files: {len(r_files)}"))
            self.files.append({
                'a0': os.path.join(a0_dir, note_file),
                'r': r_files,
                'item': item,
                'name': base_name  # Przechowuj pełną nazwę (np. "036-c")
            })
            
        self.status.set(f"Found {len(self.files)} samples in A0 folder")

    def check_queue(self):
        try:
            while True:
                msg = self.progress_queue.get_nowait()
                if msg[0] == 'update':
                    item, status = msg[1], msg[2]
                    self.tree.item(item, values=(status,))
                elif msg[0] == 'success':
                    self.status.set(f"Saved: {msg[1]}")
                elif msg[0] == 'error':
                    self.status.set(f"Error: {msg[1]}")
                elif msg[0] == 'done':
                    # Re-enable buttons after processing
                    for child in self.root.winfo_children():
                        if isinstance(child, ttk.Button):
                            child.configure(state='normal')
                    self.status.set("Processing completed")
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)

    def process_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        files_to_process = []
        for item in selected_items:
            for file_info in self.files:
                if file_info['item'] == item:
                    files_to_process.append(file_info)
                    break
                    
        self._process_files(files_to_process)

    def process_all(self):
        self._process_files(self.files)

    def _process_files(self, files_to_process):
        output_dir = self.output_dir.get()
        if not output_dir:
            self.status.set("Please select output directory")
            return
            
        os.makedirs(output_dir, exist_ok=True)
        
        # Disable buttons during processing
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Button):
                child.configure(state='disabled')
        
        # Start processing thread
        Thread(target=self._processing_thread, args=(files_to_process,), daemon=True).start()
        
    def _processing_thread(self, files_to_process):
        for file_info in files_to_process:
            # Zachowaj oryginalną nazwę pliku (np. "036-c") i dodaj "-full.wav"
            original_name = os.path.splitext(os.path.basename(file_info['a0']))[0]
            output_path = os.path.join(self.output_dir.get(), f"{original_name}-full.wav")
            
            self.progress_queue.put(('update', file_info['item'], 'Processing...'))
            
            success = self.denoiser.process_note(
                file_info['a0'],
                file_info['r'],
                output_path,
                self.strength.get(),
                self.progress_queue
            )
            
            if success:
                self.progress_queue.put(('update', file_info['item'], 'Completed'))
            else:
                self.progress_queue.put(('update', file_info['item'], 'Failed'))
        
        self.progress_queue.put(('done',))

if __name__ == "__main__":
    root = tk.Tk()
    app = DenoiserGUI(root)
    root.mainloop()