import numpy as np  
import matplotlib.pyplot as plt 

class HarmonicOscillator:  
    """  
    Oscylator harmoniczny z dynamiczną modulacją częstotliwości, zgodny z Rys. 4-6 patentu, blok 14.  

    Attributes:  
        f0 (float): Częstotliwość podstawowa [Hz].  
        fs (int): Częstotliwość próbkowania [Hz].  
        modulation_depth (float): Głębokość modulacji częstotliwości (0.0 do 1.0).  
    """  
    def __init__(self, f0, fs, modulation_depth=0.01):  
        self.f0 = f0  
        self.fs = fs  
        self.mod_depth = modulation_depth  
        self.x = [0, np.sin(2 * np.pi * f0 / fs)]  # Zmienne stanu (Rys. 4)
        self.t = 0
        self.dt = 1.0 / self.fs

    def _update_frequency(self, t):  
        """Modulacja częstotliwości (Rys. 5, 6, 9)."""  
        # Deterministiczna modulacja (np. LFO)  
        lfo = 0.1 * np.sin(2 * np.pi * 5 * t)  # Przykład z Rys. 8  
        # Losowa fluktuacja (Rys. 6)  
        noise = self.mod_depth * np.random.uniform(-1, 1)  
        return self.f0 * (1 + lfo + noise)  

    def __iter__(self):
        return self

    def __next__(self):  
        # Aktualizacja częstotliwości (Rys. 5)  
        current_freq = self._update_frequency(self.t)  
        alpha = 2 * np.cos(2 * np.pi * current_freq / self.fs)  

        # Generowanie próbki (Rys. 4)  
        x_new = alpha * self.x[1] - self.x[0]  
        self.x = [self.x[1], x_new]  
        self.t += self.dt
        return x_new

if __name__ == "__main__":
    # Konfiguracja
    f0 = 440
    fs = 44100  # Poprawione: 44.1 kHz powinno być zapisane jako 44100
    duration = 0.1  # Skrócony czas dla lepszej wizualizacji
    
    oscillator = HarmonicOscillator(f0, fs)
    samples = [next(oscillator) for _ in range(int(duration * fs))]

    # Wizualizacja
    plt.plot(samples[:1000])  
    plt.title("Sygnał wyjściowy oscylatora (z modulacją)")  
    plt.xlabel("Próbki")  
    plt.ylabel("Amplituda")  
    plt.show()