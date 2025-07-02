import numpy as np
import scipy.signal as sig

class PhysicalModelOrgan:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.harmonic_gen = HarmonicGenerator(sample_rate)
        self.noise_gen = NoiseGenerator(sample_rate)
        self.resonator = LinearResonator(sample_rate)
        self.params = self.default_params()
        
    def default_params(self):
        '''Parametry zgodne z patentem'''
        return {
            # ===== GENERATOR HARMONICZNY (Fig. 3) =====
            'CLIP1': 0.7,  # Ogranicznik amplitudy w ścieżce 1 (19a)
            'CLIP2': 0.5,  # Ogranicznik amplitudy w ścieżce 2 (19b)
            'GAIN1': 1.0,  # Wzmocnienie ścieżki 1 (18a)
            'GAIN2': 0.8,  # Wzmocnienie ścieżki 2 (18b)
            
            # Blok sumatora (28):
            'GAIND': 0.6,  # Wzmocnienie ścieżki bezpośredniej
            'GAINF': 0.4,  # Wzmocnienie ścieżki filtrowanej
            
            # Linia opóźnienia (24) i suma (25):
            'CDEL': 0.3,   # Wzmocnienie składowej opóźnionej
            'CBYP': 0.7,   # Wzmocnienie składowej bezpośredniej
            
            # Oscylator harmoniczny (Fig. 4):
            'epsilon': 1e-5,  # Współczynnik stabilizacji (30)
            
            # ===== GENERATOR SZUMU (Fig. 10-12) =====
            'NGAIN': 0.5,   # Wzmocnienie wyjściowe szumu (NGAIN w Fig. 11)
            'NBFBK': 0.4,   # Współczynnik sprzężenia zwrotnego (NBFBK)
            'NCGAIN': 0.6,  # Wzmocnienie w pętli (NCGAIN)
            
            # Generator RATE (Fig. 10):
            'RTGAIN': 1.2,  # Wzmocnienie wejściowe (RTGAIN)
            
            # ===== REZONATOR LINIOWY (Fig. 15) =====
            'FBK': 0.85,    # Wzmocnienie pętli sprzężenia zwrotnego
            'TFBK': 1.0,    # Typ piszczałki (+1 otwarta, -1 zamknięta) (53)
            
            # ===== OBIEDNIE =====
            # Obwiednia harmoniczna (Fig. 7):
            'attack_time': 0.1,      # Czas ataku (T1)
            'sustain_level': 0.8,    # Poziom podtrzymania (L2)
            'release_time': 0.3,     # Czas wybrzmienia (T4)
            
            # Obwiednia szumu (Fig. 13):
            'NBL0': 0.0,     # Poziom początkowy
            'NBL1': 1.0,     # Poziom po ataku
            'NBT': 0.05,     # Czas narastania
            
            # Obwiednia dodatkowa (Fig. 14):
            'NL0': 0.0,      # Poziom początkowy
            'NL1': 0.5,      # Poziom pośredni
            'NL2': 0.3,      # Poziom końcowy
            'NT1': 0.05,     # Czas do NL1
            'NT2': 0.1,      # Czas do NL2
            'NT3': 0.2       # Czas wybrzmienia
        }