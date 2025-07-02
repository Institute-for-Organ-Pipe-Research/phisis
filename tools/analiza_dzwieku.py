import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import scipy.io.wavfile as wavfile
import tkinter as tk
from tkinter import filedialog, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AudioAnalyzerApp:
    def __init__(self, master):
        self.master = master
        master.title("Audio Analysis Tool")

        # Przycisk wczytania pliku
        self.load_button = tk.Button(master, text="Wczytaj plik WAV", command=self.load_file)
        self.load_button.pack(pady=5)

        # Suwak progu amplitudy harmonicznych
        self.threshold_label = tk.Label(master, text="Próg harmonicznych")
        self.threshold_label.pack()
        self.threshold_scale = tk.Scale(master, from_=0.01, to=1.0, resolution=0.01,
                                        orient=tk.HORIZONTAL, command=self.update_plots)
        self.threshold_scale.set(0.05)
        self.threshold_scale.pack(fill=tk.X, padx=10)

        # Pole tekstowe na informacje o harmonicznych (kopiowalne)
        self.info_text = scrolledtext.ScrolledText(master, height=8, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Ramka na wykresy matplotlib
        self.fig, self.axs = plt.subplots(3, 1, figsize=(8, 6))
        self.fig.tight_layout(pad=3.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Dane audio
        self.fs = None
        self.data = None

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if not file_path:
            return
        self.fs, data = wavfile.read(file_path)
        if data.ndim > 1:
            data = data[:, 0]
        self.data = data / np.max(np.abs(data))  # normalizacja
        self.update_plots()

    def detect_fundamental_frequency(self, data):
        freqs, psd = signal.periodogram(data, self.fs)
        fundamental_idx = np.argmax(psd[1:]) + 1  # pomijamy DC
        return freqs[fundamental_idx]

    def detect_harmonics(self, fundamental_freq, fft_data, freqs, threshold):
        harmonics = []
        for n in range(1, 21):
            target_freq = fundamental_freq * n
            idx = np.argmin(np.abs(freqs - target_freq))
            if idx < len(fft_data) and fft_data[idx] > threshold * np.max(fft_data):
                harmonics.append((n, freqs[idx], fft_data[idx]))
        return harmonics

    def update_plots(self, event=None):
        if self.data is None:
            return

        n_samples = len(self.data)
        time = np.arange(n_samples) / self.fs
        fft_data = np.abs(np.fft.rfft(self.data))
        freqs = np.fft.rfftfreq(n_samples, 1/self.fs)
        f_spect, t_spect, Sxx = signal.spectrogram(self.data, fs=self.fs, nperseg=1024)

        # Czyścimy wykresy
        for ax in self.axs:
            ax.clear()

        # Wykres czasowy
        self.axs[0].plot(time, self.data, color='blue')
        self.axs[0].set_title("Wykres czasowy sygnału")
        self.axs[0].set_xlabel("Czas [s]")
        self.axs[0].set_ylabel("Amplituda")
        self.axs[0].grid(True)

        # FFT
        self.axs[1].plot(freqs, fft_data, color='green')
        self.axs[1].set_title("Widmo częstotliwościowe (FFT)")
        self.axs[1].set_xlabel("Częstotliwość [Hz]")
        self.axs[1].set_ylabel("Amplituda")
        self.axs[1].set_xlim(0, 5000)
        self.axs[1].grid(True)

        # Detekcja f0 i harmonicznych
        f0 = self.detect_fundamental_frequency(self.data)
        threshold = self.threshold_scale.get()
        harmonics = self.detect_harmonics(f0, fft_data, freqs, threshold)
        for n, freq, amp in harmonics:
            self.axs[1].axvline(x=freq, color='red', linestyle='--', alpha=0.6)

        # Spektrogram
        im = self.axs[2].pcolormesh(t_spect, f_spect, 10 * np.log10(Sxx + 1e-12), shading='gouraud', cmap='inferno')
        self.axs[2].set_title("Spektrogram")
        self.axs[2].set_xlabel("Czas [s]")
        self.axs[2].set_ylabel("Częstotliwość [Hz]")
        self.axs[2].grid(True)
        self.fig.colorbar(im, ax=self.axs[2], format='%+2.0f dB')

        # Aktualizacja tekstu z informacjami o harmonicznych
        info_text = f"Częstotliwość podstawowa: {f0:.2f} Hz\nHarmoniczne:\n"
        for n, freq, amp in harmonics:
            info_text += f"  {n}x: {freq:.2f} Hz (amp: {amp:.2f})\n"
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info_text)

        # Odświeżenie canvas
        self.canvas.draw_idle()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioAnalyzerApp(root)
    root.mainloop()
