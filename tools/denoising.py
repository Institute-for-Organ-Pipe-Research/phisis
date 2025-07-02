import os
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog
import numpy as np
from scipy import signal, fft
import soundfile as sf
from threading import Thread
import queue
from scipy.signal import butter, filtfilt

class PipeDenoiser:
    def __init__(self):
        self.sr = 44100
        self.settings = {
            'strength': 0.75,
            'extra_strength': 0.15,
            'window_size': 4096,
            'hp_filter': True,
            'crossfade': 1.0,
            'generate_synthetic_r': False,
            'synthetic_r_from_sustain': False
        }
        
    def normalize(self, audio):
        peak = np.max(np.abs(audio))
        if peak > 0:
            return audio / peak
        return audio
    
    def apply_fade(self, audio, fade_len=500):
        if fade_len <= 0 or len(audio) < 10:
            return audio
            
        if len(audio) > fade_len:
            fade_in = np.linspace(0, 1, fade_len)
            audio[:fade_len] *= fade_in
        else:
            fade_in = np.linspace(0, 1, len(audio))
            audio *= fade_in
        
        if len(audio) > fade_len:
            fade_out = np.linspace(1, 0, fade_len)
            audio[-fade_len:] *= fade_out
        else:
            fade_out = np.linspace(1, 0, len(audio))
            audio *= fade_out
        
        return audio
        
    def remove_reverb(self, audio, strength=0.75):
        window_size = self.settings['window_size']
        hop_size = window_size // 4
        window = signal.windows.hann(window_size)
        
        clean_audio = np.zeros(len(audio))
        weight = np.zeros(len(audio))
        
        for i in range(0, len(audio) - window_size, hop_size):
            frame = audio[i:i+window_size] * window
            
            spectrum = fft.rfft(frame)
            magnitude = np.abs(spectrum)
            phase = np.angle(spectrum)
            
            threshold = np.percentile(magnitude, 40 * (1 - strength))
            mask = np.where(magnitude > threshold, 1, np.power(magnitude / (threshold + 1e-10), 0.3))
            
            clean_magnitude = magnitude * mask
            clean_spectrum = clean_magnitude * np.exp(1j * phase)
            clean_frame = np.real(fft.irfft(clean_spectrum))
            
            clean_audio[i:i+window_size] += clean_frame * window
            weight[i:i+window_size] += window
        
        weight[weight < 1e-10] = 1.0
        clean_audio /= weight
        
        if self.settings['hp_filter']:
            b, a = butter(4, 40/(self.sr/2), 'highpass')
            clean_audio = filtfilt(b, a, clean_audio)
        
        return self.normalize(clean_audio)
    
    def generate_synthetic_r(self, length_samples):
        white_noise = np.random.randn(length_samples)
        b, a = butter(2, 4000 / (self.sr / 2), btype='low')
        pink_like_noise = filtfilt(b, a, white_noise)
        pink_like_noise = self.normalize(pink_like_noise)
        fade_len = int(self.sr * 0.5)
        if fade_len > length_samples:
            fade_len = length_samples
        fade = np.linspace(1, 0, fade_len)
        pink_like_noise[-fade_len:] *= fade
        return pink_like_noise

    def generate_r_from_sustain(self, sustain_audio, sr, length_sec=0.5):
        length_samples = int(sr * length_sec)
        if len(sustain_audio) < length_samples:
            tail = sustain_audio.copy()
        else:
            tail = sustain_audio[-length_samples:].copy()
        
        tail = self.normalize(tail)
        fade = np.linspace(1, 0, length_samples)
        tail *= fade
        
        b, a = butter(2, 300 / (sr / 2), btype='highpass')
        tail = filtfilt(b, a, tail)
        
        tail = self.normalize(tail)
        return tail

    def process_note(self, a0_path, r_paths, output_path, progress_queue=None):
        try:
            a0_audio, sr = sf.read(a0_path)
            if a0_audio.ndim > 1:
                a0_audio = np.mean(a0_audio, axis=1)
            self.sr = sr

            a0_audio = self.normalize(a0_audio)
            fade_len = int(0.05 * sr)
            a0_audio = self.apply_fade(a0_audio, fade_len)

            r_audios = []
            for r_path in r_paths:
                if os.path.exists(r_path):
                    r_audio, r_sr = sf.read(r_path)
                    if r_audio.ndim > 1:
                        r_audio = np.mean(r_audio, axis=1)
                    if r_sr != sr:
                        r_audio = signal.resample(r_audio, int(len(r_audio) * sr / r_sr))
                    
                    r_audio = self.remove_reverb(r_audio, self.settings['strength'])
                    r_audio = self.apply_fade(r_audio, fade_len)
                    r_audios.append(self.normalize(r_audio))
            
            avg_r = np.zeros(0)

            # Jeśli włączona opcja generowania syntetycznego R z fazy Sustain
            if self.settings.get('synthetic_r_from_sustain', False):
                avg_r = self.generate_r_from_sustain(a0_audio, sr, length_sec=0.5)
            # W przeciwnym wypadku jeśli nie ma plików R lub wybrana opcja generowania syntetycznego R (szum)
            elif self.settings.get('generate_synthetic_r', False) or not r_audios:
                length = int(0.5 * sr)
                avg_r = self.generate_synthetic_r(length)
            else:
                max_len = max(len(r) for r in r_audios) if r_audios else 0
                if max_len > 0:
                    avg_r = np.zeros(max_len)
                    for r in r_audios:
                        padded = np.pad(r, (0, max_len - len(r)), mode='constant')
                        avg_r += padded
                    avg_r /= len(r_audios)
                    avg_r = self.normalize(avg_r)
                    extra_strength = min(self.settings['strength'] + self.settings['extra_strength'], 0.95)
                    avg_r = self.remove_reverb(avg_r, extra_strength)
            
            if len(avg_r) > 0:
                crossfade = min(int(self.settings['crossfade'] * sr), len(a0_audio)//3, len(avg_r)//3)
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

            combined = self.apply_fade(combined, int(0.1 * sr))
            sf.write(output_path, combined, sr)

            if progress_queue:
                progress_queue.put(('success', os.path.basename(output_path)))
            return True

        except Exception as e:
            if progress_queue:
                progress_queue.put(('error', f"{os.path.basename(a0_path)}: {str(e)}"))
            return False


class SettingsDialog(tk.simpledialog.Dialog):
    def __init__(self, parent, settings):
        self.settings = settings
        super().__init__(parent, "Zaawansowane ustawienia")
        
    def body(self, master):
        ttk.Label(master, text="Siła redukcji głównej (0.1-0.9):").grid(row=0, sticky=tk.W)
        self.strength = tk.DoubleVar(value=self.settings['strength'])
        ttk.Scale(master, from_=0.1, to=0.9, variable=self.strength, 
                 orient=tk.HORIZONTAL, length=200).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(master, textvariable=self.strength).grid(row=0, column=2)
        
        ttk.Label(master, text="Dodatkowa siła dla R (0.0-0.3):").grid(row=1, sticky=tk.W)
        self.extra = tk.DoubleVar(value=self.settings['extra_strength'])
        ttk.Scale(master, from_=0.0, to=0.3, variable=self.extra, 
                 orient=tk.HORIZONTAL, length=200).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(master, textvariable=self.extra).grid(row=1, column=2)
        
        ttk.Label(master, text="Rozmiar okna analizy:").grid(row=2, sticky=tk.W)
        self.window = tk.IntVar(value=self.settings['window_size'])
        ttk.Combobox(master, textvariable=self.window, 
                    values=[1024, 2048, 4096, 8192], width=8).grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(master, text="Crossfade (sekundy):").grid(row=3, sticky=tk.W)
        self.crossfade = tk.DoubleVar(value=self.settings['crossfade'])
        ttk.Spinbox(master, from_=0.1, to=3.0, increment=0.1, 
                   textvariable=self.crossfade, width=5).grid(row=3, column=1, sticky=tk.W)
        
        self.hp_var = tk.BooleanVar(value=self.settings['hp_filter'])
        ttk.Checkbutton(master, text="Filtr wysokoprzepustowy (40 Hz)", 
                       variable=self.hp_var).grid(row=4, column=0, columnspan=2, sticky=tk.W)

        # Nowa opcja generowania syntetycznego R (szum)
        self.gen_synthetic_r_var = tk.BooleanVar(value=self.settings.get('generate_synthetic_r', False))
        ttk.Checkbutton(master, text="Generuj syntetyczne R (szum)", variable=self.gen_synthetic_r_var).grid(row=5, column=0, columnspan=2, sticky=tk.W)

        # Nowa opcja generowania syntetycznego R z fazy Sustain
        self.gen_sustain_r_var = tk.BooleanVar(value=self.settings.get('synthetic_r_from_sustain', False))
        ttk.Checkbutton(master, text="Generuj syntetyczne R z fazy Sustain (ogon)", variable=self.gen_sustain_r_var).grid(row=6, column=0, columnspan=2, sticky=tk.W)

        return master
    
    def apply(self):
        self.settings['strength'] = round(self.strength.get(), 2)
        self.settings['extra_strength'] = round(self.extra.get(), 2)
        self.settings['window_size'] = self.window.get()
        self.settings['hp_filter'] = self.hp_var.get()
        self.settings['crossfade'] = self.crossfade.get()
        self.settings['generate_synthetic_r'] = self.gen_synthetic_r_var.get()
        self.settings['synthetic_r_from_sustain'] = self.gen_sustain_r_var.get()


class DenoiserGUI:
    def __init__(self, root):
        self.root = root
        root.title("Organ Pipe Denoiser")
        root.geometry("1200x800")
        
        self.denoiser = PipeDenoiser()
        self.progress_queue = queue.Queue()
        
        self.root_dir = tk.StringVar()
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "denoised_output"))
        self.status = tk.StringVar(value="Gotowy")
        self.files = []
        self.check_vars = []
        
        self.create_widgets()
        self.check_queue()
        
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(top_frame, text="Ustawienia", command=self.open_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Zaznacz wszystkie", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Odznacz wszystkie", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        
        dir_frame = ttk.LabelFrame(main_frame, text="Foldery")
        dir_frame.pack(fill=tk.X, pady=5)
        
        row = 0
        ttk.Label(dir_frame, text="Główny folder:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        root_entry = ttk.Entry(dir_frame, textvariable=self.root_dir, width=70)
        root_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(dir_frame, text="Przeglądaj...", command=self.browse_root).grid(row=row, column=2, padx=5, pady=5)
        
        row += 1
        ttk.Label(dir_frame, text="Folder wyjściowy:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        output_entry = ttk.Entry(dir_frame, textvariable=self.output_dir, width=70)
        output_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(dir_frame, text="Przeglądaj...", command=self.browse_output).grid(row=row, column=2, padx=5, pady=5)
        
        row += 1
        ttk.Button(dir_frame, text="Odśwież listę", command=self.refresh_list).grid(
            row=row, column=0, columnspan=3, pady=10)
        
        dir_frame.columnconfigure(1, weight=1)
        
        list_frame = ttk.LabelFrame(main_frame, text="Próbki dźwiękowe")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        self.scrollable_frame = ttk.Frame(canvas)
        def configure_scrollregion(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.scrollable_frame.bind("<Configure>", configure_scrollregion)
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=10)
        
        self.process_btn = ttk.Button(
            bottom_frame, text="Przetwórz zaznaczone", 
            command=self.process_selected, width=20
        )
        self.process_btn.pack(side=tk.LEFT, padx=10)
        
        self.process_all_btn = ttk.Button(
            bottom_frame, text="Przetwórz wszystkie", 
            command=self.process_all, width=20
        )
        self.process_all_btn.pack(side=tk.LEFT, padx=10)
        
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(status_frame, text="Status:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=(10, 5))
        self.status_label = ttk.Label(status_frame, textvariable=self.status, foreground="blue")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

    def open_settings(self):
        SettingsDialog(self.root, self.denoiser.settings)
        
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
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.files = []
        self.check_vars = []
        
        root_dir = self.root_dir.get()
        if not root_dir or not os.path.exists(root_dir):
            self.status.set("Błąd: Nie znaleziono folderu głównego")
            return
            
        a0_dir = os.path.join(root_dir, "A0")
        if not os.path.exists(a0_dir):
            self.status.set("Błąd: Nie znaleziono folderu A0")
            return
            
        note_files = [f for f in os.listdir(a0_dir) if f.endswith('.wav')]
        
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(header_frame, text="Przetwarzaj", width=8).pack(side=tk.LEFT, padx=10)
        ttk.Label(header_frame, text="Nazwa próbki", width=40).pack(side=tk.LEFT, padx=10)
        ttk.Label(header_frame, text="Pliki R", width=10).pack(side=tk.LEFT, padx=10)
        ttk.Label(header_frame, text="Status", width=30).pack(side=tk.LEFT, padx=10)
        
        for note_file in sorted(note_files):
            base_name = os.path.splitext(note_file)[0]
            
            r_files = []
            for r_dir in ["R0", "R1", "R2", "R3"]:
                r_path = os.path.join(root_dir, r_dir, note_file)
                if os.path.exists(r_path):
                    r_files.append(r_path)
            
            item_frame = ttk.Frame(self.scrollable_frame)
            item_frame.pack(fill=tk.X, pady=3)
            
            chk_var = tk.BooleanVar(value=True)
            self.check_vars.append(chk_var)
            chk = ttk.Checkbutton(item_frame, variable=chk_var)
            chk.pack(side=tk.LEFT, padx=10)
            
            ttk.Label(item_frame, text=base_name, width=45, anchor="w").pack(side=tk.LEFT, padx=10)
            ttk.Label(item_frame, text=str(len(r_files)), width=10, anchor="center").pack(side=tk.LEFT, padx=10)
            
            status_var = tk.StringVar(value="Gotowy")
            status_label = ttk.Label(item_frame, textvariable=status_var, width=35, anchor="w", foreground="blue")
            status_label.pack(side=tk.LEFT, padx=10)
            
            self.files.append({
                'a0': os.path.join(a0_dir, note_file),
                'r': r_files,
                'status_var': status_var,
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
                    self.files[idx]['status_var'].set(status)
                    if "Przetwarzanie" in status:
                        self.files[idx]['label'].configure(foreground="blue")
                    elif "Gotowy" in status or "Zakończono" in status:
                        self.files[idx]['label'].configure(foreground="green")
                    elif "Błąd" in status:
                        self.files[idx]['label'].configure(foreground="red")
                elif msg[0] == 'success':
                    self.status.set(f"Przetworzono: {msg[1]}")
                elif msg[0] == 'error':
                    self.status.set(f"Błąd: {msg[1]}")
                self.progress_queue.task_done()
        except queue.Empty:
            pass
        self.root.after(200, self.check_queue)

    def worker(self, idx):
        file_info = self.files[idx]
        self.progress_queue.put(('update', idx, "Przetwarzanie..."))
        output_filename = file_info['name'] + "_denoised.wav"
        output_path = os.path.join(self.output_dir.get(), output_filename)
        success = self.denoiser.process_note(
            file_info['a0'], file_info['r'], output_path, self.progress_queue)
        if success:
            self.progress_queue.put(('update', idx, "Gotowy"))
        else:
            self.progress_queue.put(('update', idx, "Błąd"))
    
    def process_selected(self):
        if not os.path.exists(self.output_dir.get()):
            os.makedirs(self.output_dir.get())
        
        for idx, var in enumerate(self.check_vars):
            if var.get():
                Thread(target=self.worker, args=(idx,), daemon=True).start()
        
    def process_all(self):
        if not os.path.exists(self.output_dir.get()):
            os.makedirs(self.output_dir.get())
        
        for idx in range(len(self.files)):
            Thread(target=self.worker, args=(idx,), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = DenoiserGUI(root)
    root.mainloop()
