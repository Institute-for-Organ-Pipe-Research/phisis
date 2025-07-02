import os
import tkinter as tk
from tkinter import filedialog, ttk
import numpy as np
from scipy import signal, fft
import soundfile as sf
from threading import Thread
import queue

class PipeDenoiser:
    def __init__(self):
        self.sr = 44100
        
    def normalize(self, audio):
        """Normalizacja amplitudy do zakresu [-1, 1]"""
        peak = np.max(np.abs(audio))
        if peak > 0:
            return audio / peak
        return audio
    
    def apply_fade(self, audio, fade_len=500):
        """Stosuje fade-in i fade-out do nagrania"""
        if fade_len <= 0 or len(audio) < 10:
            return audio
            
        # Fade-in na początku
        if len(audio) > fade_len:
            fade_in = np.linspace(0, 1, fade_len)
            audio[:fade_len] = audio[:fade_len] * fade_in
        else:
            fade_in = np.linspace(0, 1, len(audio))
            audio = audio * fade_in
        
        # Fade-out na końcu
        if len(audio) > fade_len:
            fade_out = np.linspace(1, 0, fade_len)
            audio[-fade_len:] = audio[-fade_len:] * fade_out
        else:
            fade_out = np.linspace(1, 0, len(audio))
            audio = audio * fade_out
        
        return audio
        
    def remove_reverb(self, audio, strength=0.75):
        """
        Redukcja pogłosu z zachowaniem jakości dźwięku
        """
        window_size = 2048
        hop_size = 512
        window = signal.windows.hann(window_size)
        
        clean_audio = np.zeros(len(audio))
        weight = np.zeros(len(audio))
        
        # Przetwarzaj w blokach z nakładaniem
        for i in range(0, len(audio) - window_size, hop_size):
            frame = audio[i:i+window_size] * window
            
            spectrum = fft.rfft(frame)
            magnitude = np.abs(spectrum)
            phase = np.angle(spectrum)
            
            # Szacuj pogłos jako składowe o niskiej amplitudzie
            threshold = np.percentile(magnitude, 40 * (1 - strength))
            
            # Miękka maska dla płynniejszego przejścia
            mask = np.where(magnitude > threshold, 
                           1, 
                           np.power(magnitude / (threshold + 1e-10), 0.5))
            
            # Odfiltruj składowe pogłosu
            clean_magnitude = magnitude * mask
            clean_spectrum = clean_magnitude * np.exp(1j * phase)
            clean_frame = np.real(fft.irfft(clean_spectrum))
            
            # Nakładanie z oknem
            clean_audio[i:i+window_size] += clean_frame * window
            weight[i:i+window_size] += window
        
        # Normalizacja wag
        weight[weight < 1e-10] = 1.0
        clean_audio = clean_audio / weight
        
        return self.normalize(clean_audio)

    def process_note(self, a0_path, r_paths, output_path, strength=0.75, progress_queue=None):
        try:
            # Wczytaj próbkę A0
            a0_audio, sr = sf.read(a0_path)
            if a0_audio.ndim > 1:
                a0_audio = np.mean(a0_audio, axis=1)
            self.sr = sr

            # Normalizuj A0
            a0_audio = self.normalize(a0_audio)
            
            # Zastosuj fade-out do A0
            fade_len = int(0.05 * sr)
            a0_audio = self.apply_fade(a0_audio, fade_len)

            # Wczytaj i przetwórz próbki R
            r_audios = []
            for r_path in r_paths:
                if os.path.exists(r_path):
                    r_audio, r_sr = sf.read(r_path)
                    if r_audio.ndim > 1:
                        r_audio = np.mean(r_audio, axis=1)
                    if r_sr != sr:
                        r_audio = signal.resample(r_audio, int(len(r_audio) * sr / r_sr))
                    
                    # Usuń pogłos z każdej próbki R osobno
                    r_audio = self.remove_reverb(r_audio, strength)
                    
                    # Zastosuj fade-in i fade-out
                    r_audio = self.apply_fade(r_audio, fade_len)
                    r_audios.append(self.normalize(r_audio))

            # Uśrednij próbki R
            avg_r = np.zeros(0)
            if r_audios:
                max_len = max(len(r) for r in r_audios)
                avg_r = np.zeros(max_len)
                for r in r_audios:
                    # Dopasuj długość do najdłuższego R
                    padded = np.pad(r, (0, max_len - len(r)), mode='constant')
                    avg_r += padded
                avg_r /= len(r_audios)
                avg_r = self.normalize(avg_r)

            # Połącz A0 z uśrednionym R
            if len(avg_r) > 0:
                # Crossfade 1 sekunda
                crossfade = min(int(1.0 * sr), len(a0_audio)//3, len(avg_r)//3)
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

            # Ostateczne wygładzenie połączenia
            combined = self.apply_fade(combined, int(0.1 * sr))

            # Zapisz wynik
            sf.write(output_path, combined, sr)
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
        root.geometry("1000x700")
        
        self.denoiser = PipeDenoiser()
        self.progress_queue = queue.Queue()
        
        # Variables
        self.root_dir = tk.StringVar()
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "denoised_output"))
        self.strength = tk.DoubleVar(value=0.75)
        self.status = tk.StringVar(value="Gotowy")
        self.files = []
        self.check_vars = []  # Przechowuje zmienne dla checkboxów
        
        # GUI Setup
        self.create_widgets()
        self.check_queue()

    def create_widgets(self):
        # Frame for directory selection
        dir_frame = ttk.Frame(self.root, padding="10")
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Root directory
        ttk.Label(dir_frame, text="Główny folder:").grid(row=0, column=0, sticky=tk.W)
        root_entry = ttk.Entry(dir_frame, textvariable=self.root_dir, width=50)
        root_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Button(dir_frame, text="Przeglądaj...", command=self.browse_root).grid(row=0, column=2)
        
        # Output directory
        ttk.Label(dir_frame, text="Folder wyjściowy:").grid(row=1, column=0, sticky=tk.W)
        output_entry = ttk.Entry(dir_frame, textvariable=self.output_dir, width=50)
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))
        ttk.Button(dir_frame, text="Przeglądaj...", command=self.browse_output).grid(row=1, column=2)
        
        # Refresh button
        ttk.Button(dir_frame, text="Odśwież listę", command=self.refresh_list).grid(row=2, column=0, columnspan=3, pady=5)
        
        # List frame with checkboxes
        list_frame = ttk.LabelFrame(self.root, text="Próbki dźwiękowe", padding="10")
        list_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.W, tk.E), padx=10, pady=5)
        
        # Canvas for scrollable area
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.list_container = scrollable_frame
        
        # Selection buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Zaznacz wszystkie", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Odznacz wszystkie", command=self.deselect_all).pack(side=tk.LEFT)
        
        # Processing controls
        ctrl_frame = ttk.Frame(self.root, padding="10")
        ctrl_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(ctrl_frame, text="Siła redukcji pogłosu (mniej = łagodniej):").grid(row=0, column=0)
        strength_slider = ttk.Scale(ctrl_frame, from_=0.1, to=1.0, variable=self.strength)
        strength_slider.grid(row=0, column=1, padx=5)
        
        # Value display
        value_label = ttk.Label(ctrl_frame, text=f"{self.strength.get():.2f}")
        value_label.grid(row=0, column=2)
        
        # Update label when slider moves
        def update_label(event):
            value_label.config(text=f"{self.strength.get():.2f}")
        strength_slider.bind("<Motion>", update_label)
        
        # Process buttons
        btn_frame2 = ttk.Frame(ctrl_frame)
        btn_frame2.grid(row=0, column=3, columnspan=2, padx=10)
        
        self.process_btn = ttk.Button(btn_frame2, text="Przetwórz zaznaczone", command=self.process_selected)
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        self.process_all_btn = ttk.Button(btn_frame2, text="Przetwórz wszystkie", command=self.process_all)
        self.process_all_btn.pack(side=tk.LEFT)
        
        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        ttk.Label(status_frame, text="Status:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=(10, 5))
        self.status_label = ttk.Label(status_frame, textvariable=self.status, foreground="blue")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

    def browse_root(self):
        directory = filedialog.askdirectory(title="Wybierz folder główny")
        if directory:
            self.root_dir.set(directory)
            self.refresh_list()

    def browse_output(self):
        directory = filedialog.askdirectory(title="Wybierz folder wyjściowy")
        if directory:
            self.output_dir.set(directory)

    def refresh_list(self):
        # Clear existing list
        for widget in self.list_container.winfo_children():
            widget.destroy()
        
        self.files = []
        self.check_vars = []
        
        root_dir = self.root_dir.get()
        if not root_dir or not os.path.exists(root_dir):
            return
            
        a0_dir = os.path.join(root_dir, "A0")
        if not os.path.exists(a0_dir):
            self.status.set("Błąd: Nie znaleziono folderu A0")
            return
            
        # Find all note files in A0
        note_files = [f for f in os.listdir(a0_dir) if f.endswith('.wav')]
        
        # Header
        header_frame = ttk.Frame(self.list_container)
        header_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(header_frame, text="Przetwarzaj", width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Nazwa próbki", width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Pliki R", width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Status", width=15).pack(side=tk.LEFT, padx=5)
        
        for note_file in sorted(note_files):
            base_name = os.path.splitext(note_file)[0]
            
            # Find corresponding R files
            r_files = []
            for r_dir in ["R0", "R1", "R2", "R3"]:
                r_path = os.path.join(root_dir, r_dir, note_file)
                if os.path.exists(r_path):
                    r_files.append(r_path)
            
            # Create list item
            item_frame = ttk.Frame(self.list_container)
            item_frame.pack(fill=tk.X, pady=2)
            
            # Checkbox
            chk_var = tk.BooleanVar(value=True)
            self.check_vars.append(chk_var)
            chk = ttk.Checkbutton(item_frame, variable=chk_var)
            chk.pack(side=tk.LEFT, padx=5)
            
            # Sample name
            ttk.Label(item_frame, text=base_name, width=25).pack(side=tk.LEFT, padx=5)
            
            # R files count
            ttk.Label(item_frame, text=str(len(r_files)), width=10).pack(side=tk.LEFT, padx=5)
            
            # Status label
            status_var = tk.StringVar(value="Gotowy")
            status_label = ttk.Label(item_frame, textvariable=status_var, width=15)
            status_label.pack(side=tk.LEFT, padx=5)
            
            # Store file info
            self.files.append({
                'a0': os.path.join(a0_dir, note_file),
                'r': r_files,
                'status': status_var,
                'label': status_label,
                'name': base_name
            })
            
        self.status.set(f"Znaleziono {len(self.files)} próbek w folderze A0")

    def select_all(self):
        for var in self.check_vars:
            var.set(True)

    def deselect_all(self):
        for var in self.check_vars:
            var.set(False)

    def check_queue(self):
        try:
            while True:
                msg = self.progress_queue.get_nowait()
                if msg[0] == 'update':
                    idx, status = msg[1], msg[2]
                    self.files[idx]['status'].set(status)
                    
                    # Update color based on status
                    if "Przetwarzanie" in status:
                        self.files[idx]['label'].configure(foreground="blue")
                    elif "Gotowy" in status:
                        self.files[idx]['label'].configure(foreground="green")
                    elif "Błąd" in status:
                        self.files[idx]['label'].configure(foreground="red")
                    elif "Zakończono" in status:
                        self.files[idx]['label'].configure(foreground="darkgreen")
                        
                elif msg[0] == 'success':
                    self.status.set(f"Zapisano: {msg[1]}")
                elif msg[0] == 'error':
                    self.status.set(f"Błąd: {msg[1]}")
                    self.status_label.configure(foreground="red")
                elif msg[0] == 'done':
                    # Re-enable buttons after processing
                    for child in self.root.winfo_children():
                        if isinstance(child, ttk.Button):
                            child.configure(state='normal')
                    self.status.set("Przetwarzanie zakończone")
                    self.status_label.configure(foreground="darkgreen")
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)

    def process_selected(self):
        files_to_process = []
        for i, file_info in enumerate(self.files):
            if self.check_vars[i].get():
                files_to_process.append((i, file_info))
                
        if not files_to_process:
            self.status.set("Błąd: Nie zaznaczono żadnych plików")
            return
            
        self._process_files(files_to_process)

    def process_all(self):
        files_to_process = [(i, f) for i, f in enumerate(self.files)]
        self._process_files(files_to_process)

    def _process_files(self, files_to_process):
        output_dir = self.output_dir.get()
        if not output_dir:
            self.status.set("Błąd: Wybierz folder wyjściowy")
            return
            
        os.makedirs(output_dir, exist_ok=True)
        
        # Disable buttons during processing
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Button):
                child.configure(state='disabled')
        
        # Start processing thread
        Thread(target=self._processing_thread, args=(files_to_process,), daemon=True).start()
        
    def _processing_thread(self, files_to_process):
        for idx, file_info in files_to_process:
            # Update status to processing
            self.progress_queue.put(('update', idx, 'Przetwarzanie...'))
            
            # Prepare output path
            original_name = os.path.splitext(os.path.basename(file_info['a0']))[0]
            output_path = os.path.join(self.output_dir.get(), f"{original_name}-full.wav")
            
            try:
                success = self.denoiser.process_note(
                    file_info['a0'],
                    file_info['r'],
                    output_path,
                    self.strength.get(),
                    self.progress_queue
                )
                
                if success:
                    self.progress_queue.put(('update', idx, 'Zakończono pomyślnie'))
                else:
                    self.progress_queue.put(('update', idx, 'Błąd przetwarzania'))
            except Exception as e:
                self.progress_queue.put(('update', idx, f'Błąd: {str(e)}'))
        
        self.progress_queue.put(('done',))

if __name__ == "__main__":
    root = tk.Tk()
    app = DenoiserGUI(root)
    root.mainloop()