import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import scipy.signal as signal
import scipy.io.wavfile as wavfile
import tkinter as tk
from tkinter import filedialog
import os

# Globalne dane pliku
loaded_data = {'fs': None, 'data': None}

# Funkcja do ładowania pliku WAV
def load_wav_file():
    root = tk.Tk()
    root.withdraw()  # Ukryj okno główne
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if not file_path:
        print("Nie wybrano pliku.")
        return None, None
    fs, data = wavfile.read(file_path)
    if data.ndim > 1:
        data = data[:, 0]  # Mono
    data = data / np.max(np.abs(data))  # Normalizacja
    return fs, data

# Funkcja do wykrywania częstotliwości podstawowej
def detect_fundamental_frequency(data, fs):
    freqs, psd = signal.periodogram(data, fs)
    fundamental_idx = np.argmax(psd[1:]) + 1  # Pomijamy DC
    return freqs[fundamental_idx]

# Funkcja do wykrywania harmonicznych
def detect_harmonics(fundamental_freq, fft_data, freqs, threshold):
    harmonics = []
    for n in range(1, 21):  # Do 20. harmonicznej
        target_freq = fundamental_freq * n
        idx = np.argmin(np.abs(freqs - target_freq))
        if idx < len(fft_data) and fft_data[idx] > threshold * np.max(fft_data):
            harmonics.append((n, freqs[idx], fft_data[idx]))
    return harmonics

# Funkcja do aktualizacji wykresów i informacji

def update_plots(fs, data):
    n_samples = len(data)
    time = np.arange(n_samples) / fs

    # FFT
    fft_data = np.abs(np.fft.rfft(data))
    freqs = np.fft.rfftfreq(n_samples, 1/fs)

    # Spektrogram
    f_spect, t_spect, Sxx = signal.spectrogram(data, fs=fs, nperseg=1024)

    # Czyszczenie poprzednich wykresów
    for ax in axs:
        ax.clear()
        ax.grid(True)

    # Wykres czasowy
    axs[0].plot(time, data, color='blue')
    axs[0].set_title("Wykres czasowy sygnału")
    axs[0].set_xlabel("Czas [s]")
    axs[0].set_ylabel("Amplituda")

    # FFT z oznaczeniem harmonicznych
    axs[1].plot(freqs, fft_data, color='green')
    axs[1].set_title("Widmo częstotliwościowe (FFT)")
    axs[1].set_xlabel("Częstotliwość [Hz]")
    axs[1].set_ylabel("Amplituda")
    axs[1].set_xlim(0, 5000)

    # Wykrywanie częstotliwości podstawowej i harmonicznych
    f0 = detect_fundamental_frequency(data, fs)
    harmonics = detect_harmonics(f0, fft_data, freqs, amp_threshold_slider.val)
    for n, freq, amp in harmonics:
        axs[1].axvline(x=freq, color='red', linestyle='--', alpha=0.6)

    # Spektrogram
    im = axs[2].pcolormesh(t_spect, f_spect, 10 * np.log10(Sxx + 1e-12), shading='gouraud', cmap='inferno')
    axs[2].set_title("Spektrogram")
    axs[2].set_xlabel("Czas [s]")
    axs[2].set_ylabel("Częstotliwość [Hz]")
    fig.colorbar(im, ax=axs[2], format='%+2.0f dB')

    # Wyświetlanie informacji
    info_text = f"Częstotliwość podstawowa: {f0:.2f} Hz\nHarmoniczne:\n"
    for n, freq, amp in harmonics:
        info_text += f"  {n}x: {freq:.2f} Hz (amp: {amp:.2f})\n"

    info_box.set_val(info_text)
    fig.canvas.draw()

# Główna część GUI
fig, axs = plt.subplots(3, 1, figsize=(12, 10), constrained_layout=True)
fig.canvas.manager.set_window_title("Analiza dźwięku - spektrogram i FFT")

# Przycisk "Wczytaj plik"
ax_button = plt.axes([0.4, 0.05, 0.2, 0.075])
button = widgets.Button(ax_button, 'Wczytaj plik WAV')

# Suwak progu amplitudy
ax_slider = plt.axes([0.15, 0.15, 0.7, 0.03])
amp_threshold_slider = widgets.Slider(ax_slider, 'Próg harmonicznych', 0.01, 1.0, valinit=0.05)

# Pole tekstowe na informację o częstotliwościach
ax_info = plt.axes([0.05, 0.01, 0.9, 0.12])
info_box = widgets.TextBox(ax_info, "Informacje:", initial="")
info_box.set_active(False)

def on_button_clicked(event):
    fs, data = load_wav_file()
    if fs is not None:
        loaded_data['fs'] = fs
        loaded_data['data'] = data
        update_plots(fs, data)

def on_slider_change(val):
    if loaded_data['fs'] is not None and loaded_data['data'] is not None:
        update_plots(loaded_data['fs'], loaded_data['data'])

button.on_clicked(on_button_clicked)
amp_threshold_slider.on_changed(on_slider_change)

plt.show()