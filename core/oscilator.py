import numpy as np
from numba import jit, float64, int64
from scipy.io.wavfile import write

# Funkcje kompatybilne z Numba
@jit(float64[:](float64, int64, float64, float64, float64, float64), nopython=True)
def generate_harmonic(f0, n_samples, fs, mod_depth, lfo_freq, clip_level):
    output = np.zeros(n_samples)
    x1, x2 = 0.0, np.sin(2 * np.pi * f0 / fs)
    
    for n in range(n_samples):
        t = n / fs
        lfo = mod_depth * np.sin(2 * np.pi * lfo_freq * t)
        noise = 0.01 * (np.random.random() * 2 - 1)
        freq = f0 * (1 + lfo + noise)
        
        alpha = 2 * np.cos(2 * np.pi * freq / fs)
        x_new = alpha * x2 - x1
        x_new = min(max(x_new * 1.001, -clip_level), clip_level)
        
        output[n] = x_new
        x1, x2 = x2, x_new
        
    return output

@jit(float64[:](float64[:], float64[:]), nopython=True)
def generate_noise(rate_signal, rng_values):
    output = np.zeros_like(rate_signal)
    prev = 0.0
    
    for n in range(len(rate_signal)):
        diff = rng_values[n] - prev
        limited = min(max(diff, -rate_signal[n]), rate_signal[n])
        output[n] = prev + limited
        prev = output[n]
        
    return output

class PhisisOrganPipe:
    def __init__(self, fs=44100):
        self.fs = fs
        self.params = {
            'f0': 440.0,
            'mod_depth': 0.007,
            'lfo_freq': 5.0,
            'nonlinear_gain': 1.8,
            'clip_level': 0.9,
            'noise_level': 0.04,
            'rate_scale': 0.3,
            'pipe_length': 2.5,
            'lp_coeffs': np.array([0.85, -0.15]),
            'hp_coeffs': np.array([0.95, -0.95]),
            'ap_coeffs': np.array([0.7, -0.7]),
            'tfbk': 0.68,
            'attack_time': 0.08,
            'decay_time': 0.15,
            'sustain_level': 0.75,
            'release_time': 0.5,
            'noise_attack': 0.02
        }
        self.init_resonator()

    def set_parameter(self, param_name, value):
        """Ustawia parametr i aktualizuje rezonator jeśli potrzebne"""
        if param_name in self.params:
            self.params[param_name] = value
            if param_name in ['pipe_length', 'lp_coeffs', 'hp_coeffs', 'ap_coeffs', 'tfbk']:
                self.init_resonator()

    def init_resonator(self):
        """Inicjalizuje rezonator z aktualnymi parametrami"""
        speed_of_sound = 343
        delay_time = (2 * self.params['pipe_length']) / speed_of_sound
        self.delay_samples = int(delay_time * self.fs)
        self.delay_line = np.zeros(self.delay_samples)
        self.delay_ptr = 0
        self.lp_state = np.zeros(2)
        self.hp_state = np.zeros(2)
        self.ap_state = np.zeros(2)
        self.res_gain = 0.0

    def generate_note(self, duration):
        """Generuje dźwięk o podanym czasie trwania"""
        n_samples = int(duration * self.fs)
        
        # Generacja harmonicznej
        harmonic = generate_harmonic(
            self.params['f0'], n_samples, self.fs,
            self.params['mod_depth'], self.params['lfo_freq'], self.params['clip_level']
        )
        
        # Nieliniowe przetwarzanie
        processed_harmonic = self.params['nonlinear_gain'] * harmonic**2 - 1
        
        # Generacja szumu
        rate_signal = np.abs(harmonic) * self.params['rate_scale'] + 0.01
        noise = generate_noise(rate_signal, np.random.uniform(-1, 1, n_samples)) * self.params['noise_level']
        
        # Rezonator
        mixed = processed_harmonic + noise
        output = self.resonator(mixed)
        
        # Obwiednia
        envelope = self.generate_envelope(n_samples)
        output = output * envelope
        return output / np.max(np.abs(output))

    def resonator(self, signal):
        """Implementacja rezonatora zgodnie z patentem"""
        output = np.zeros_like(signal)
        
        for n in range(len(signal)):
            # Aktualizacja wzmocnienia
            self.res_gain = 0.999 * self.res_gain + 0.001 * 1.0
            
            # Filtr dolnoprzepustowy
            lp_out = self.params['lp_coeffs'][0] * (signal[n] * self.res_gain) + \
                     self.params['lp_coeffs'][1] * self.lp_state[0]
            
            # Filtr górnoprzepustowy
            hp_out = self.params['hp_coeffs'][0] * lp_out + \
                     self.params['hp_coeffs'][1] * self.hp_state[0]
            
            # Filtr all-pass
            ap_out = self.params['ap_coeffs'][0] * hp_out + \
                     self.params['ap_coeffs'][1] * self.ap_state[0]
            
            # Aktualizacja stanów
            self.lp_state = np.roll(self.lp_state, 1)
            self.lp_state[0] = signal[n] * self.res_gain
            self.hp_state = np.roll(self.hp_state, 1)
            self.hp_state[0] = lp_out
            self.ap_state = np.roll(self.ap_state, 1)
            self.ap_state[0] = hp_out
            
            # Linia opóźnienia
            output[n] = self.delay_line[self.delay_ptr]
            self.delay_line[self.delay_ptr] = ap_out * self.params['tfbk']
            self.delay_ptr = (self.delay_ptr + 1) % self.delay_samples
            
        return output

    def generate_envelope(self, n_samples):
        """Generuje obwiednię ADSR z dokładnym dopasowaniem długości"""
        attack_samples = int(self.params['attack_time'] * self.fs)
        decay_samples = int(self.params['decay_time'] * self.fs)
        release_samples = int(self.params['release_time'] * self.fs)
        sustain_samples = n_samples - attack_samples - decay_samples - release_samples
        
        # Zabezpieczenie przed ujemnymi wartościami
        if sustain_samples < 0:
            total = attack_samples + decay_samples + release_samples
            attack_samples = int(attack_samples * n_samples / total)
            decay_samples = int(decay_samples * n_samples / total)
            release_samples = n_samples - attack_samples - decay_samples
            sustain_samples = 0
        
        # Generacja segmentów
        attack_env = np.linspace(0, 1, attack_samples)
        decay_env = np.linspace(1, self.params['sustain_level'], decay_samples)
        sustain_env = np.full(sustain_samples, self.params['sustain_level'])
        release_env = np.linspace(self.params['sustain_level'], 0, release_samples)
        
        # Łączenie segmentów
        envelope = np.concatenate([attack_env, decay_env, sustain_env, release_env])
        
        # Dopasowanie dokładnej długości
        return envelope[:n_samples]

# Przykład użycia
if __name__ == "__main__":
    # Inicjalizacja dla Principal 8'
    pipe = PhisisOrganPipe()
    
    # Parametry podstawowe
    pipe.set_parameter('f0', 440.0)
    pipe.set_parameter('pipe_length', 0.39)

    # Parametry modulacji i nieliniowości
    pipe.set_parameter('mod_depth', 0.005)
    pipe.set_parameter('lfo_freq', 0.2)
    pipe.set_parameter('nonlinear_gain', 1.2)
    pipe.set_parameter('clip_level', 0.8)

    # Parametry szumu
    pipe.set_parameter('noise_level', 0.015)
    pipe.set_parameter('rate_scale', 0.2)
    
    # Parametry rezonatora
    pipe.set_parameter('lp_coeffs', np.array([0.9, -0.1]) )
    pipe.set_parameter('hp_coeffs', np.array([0.85, -0.85]) )
    pipe.set_parameter('ap_coeffs', np.array([0.6, -0.6]) )
    pipe.set_parameter('tfbk', 0.9)

    # Parametry obwiedni
    pipe.set_parameter('attack_time', 0.08)
    pipe.set_parameter('decay_time', 0.15)
    pipe.set_parameter('sustain_level', 0.75)
    pipe.set_parameter('release_time', 0.5)
    pipe.set_parameter('noise_attack', 0.02)

    
    # Generacja i zapis dźwięku
    note = pipe.generate_note(4.0)
    write("principal_8ft.wav", 44100, note.astype(np.float32))