import numpy as np
import scipy.signal as sig

class PhysicalModelOrgan:
    """Implementacja patentu US7442869B2"""
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.harmonic_gen = HarmonicGenerator(sample_rate)
        self.noise_gen = NoiseGenerator(sample_rate)
        self.resonator = LinearResonator(sample_rate)
        self.params = self.default_params()
    
    def default_params(self):
        """Parametry zgodne z patentem"""
        return {
            # Parametry generatora harmonicznego (Fig. 3)
            'CLIP1': 0.7, 'CLIP2': 0.5, 'GAIN1': 1.0, 'GAIN2': 0.8,
            'GAIND': 0.6, 'GAINF': 0.4,  # Blok (28)
            'CDEL': 0.3, 'CBYP': 0.7,    # Blok (25)
            
            # Parametry szumu (Fig. 11)
            'NGAIN': 0.5, 'NBFBK': 0.4, 'NCGAIN': 0.6,
            'RATE_GAIN': 1.2,            # RTGAIN (Fig. 10)
            
            # Rezonator (Fig. 15)
            'FBK': 0.85, 'TFBK': 1.0,    # Typ piszczałki (+1/-1)
            
            # Czasy obwiedni
            'attack_time': 0.1, 'sustain_level': 0.8, 'release_time': 0.3
        }
    
    def render_note(self, freq, duration, params=None):
        if params is None:
            params = self.params
        num_samples = int(duration * self.sample_rate)
        harmonic = self.harmonic_gen.generate(freq, num_samples, params)
        noise = self.noise_gen.generate(harmonic, num_samples, params)
        output = self.resonator.process(harmonic, noise, params, num_samples)
        return output



class HarmonicGenerator:
    """Generator składowej harmonicznej (Fig. 3)"""
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.osc = HarmonicOscillator(sample_rate)
        self.env_gen = EnvelopeGenerator(sample_rate)
        
    def generate(self, freq, num_samples, params):
        output = np.zeros(num_samples)
        
        # Inicjalizacja komponentów
        delay_line = np.zeros(1024)  # Blok (24)
        delay_index = 0
        
        for i in range(num_samples):
            # Generowanie sinusoidy (14)
            sin_wave = self.osc.process(freq, params)
            
            # Nieliniowa konwersja (15)
            double_freq = 2 * sin_wave**2 - 1
            
            # Ścieżka 1 (18a, 19a)
            path1 = sin_wave * params['GAIN1']
            path1 = np.clip(path1, -params['CLIP1'], params['CLIP1'])
            
            # Ścieżka 2 (18b, 19b)
            path2 = double_freq * params['GAIN2']
            path2 = np.clip(path2, -params['CLIP2'], params['CLIP2'])
            
            # Obwiednie (20a, 20b)
            env = self.env_gen.attack_sustain_release(i, num_samples, params)
            path1 *= env
            path2 *= env
            
            # Sumator (21)
            sum_node = path1 + path2
            
            # Modulacja amplitudy (22)
            modulated = sum_node * params.get('MOD_AMPL', 1.0)
            
            # Linia opóźnienia i suma (24, 25)
            delayed = delay_line[delay_index]
            filtered = params['CBYP'] * modulated + params['CDEL'] * delayed
            
            # Nieliniowa funkcja (26)
            nonlin_out = filtered - filtered**4  # Uproszczona wersja f(x)
            
            # Filtr pasmowoprzepustowy (27)
            # (Uproszczone - w patentowe centralny na częstotliwość podstawową)
            filtered_bp = nonlin_out  # W praktyce: filtr IIR
            
            # Sumator końcowy (28)
            output[i] = params['GAIND'] * nonlin_out + params['GAINF'] * filtered_bp
            
            # Aktualizacja linii opóźnienia
            delay_line[delay_index] = modulated
            delay_index = (delay_index + 1) % len(delay_line)
            
        return output


class HarmonicOscillator:
    """Oscylator harmoniczny (Fig. 4)"""
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.var1 = 1.0  # Stan VAR1
        self.var2 = 0.0  # Stan VAR2
        
    def process(self, freq, params):
        """Implementacja równań (29)-(32) z patentu"""
        F = 2 * np.sin(np.pi * freq / self.sample_rate)
        epsilon = params.get('epsilon', 1e-5)
        
        # Równanie (29)
        self.var1 = self.var1 - F**2 * self.var2
        
        # Równanie (30)
        self.var2 = self.var2 * (1 + epsilon)
        
        # Równanie (31)
        self.var2 = self.var1 + self.var2
        
        # Równanie (32)
        self.var1 = np.clip(self.var1, -1, 1)
        
        return self.var1


class NoiseGenerator:
    """Generator składowej szumowej (Fig. 10-12)"""
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.rate_limiter = RateLimiter()
        self.env_gen = EnvelopeGenerator(sample_rate)
        
    def generate(self, harmonic_signal, num_samples, params):
        # Generowanie sygnału RATE (Fig. 10)
        rate_signal = self._generate_rate_signal(harmonic_signal, params)
        
        # Inicjalizacja "NOISE BOX" (Fig. 11)
        delay_lines = [np.zeros(100) for _ in range(4)]  # NBDL1-4
        delay_indices = [0, 0, 0, 0]
        prev_limiter_out = 0.0
        
        output = np.zeros(num_samples)
        
        for i in range(num_samples):
            # Biały szum (40)
            white_noise = np.random.uniform(-1, 1)
            
            # Filtracja dolnoprzepustowa (41)
            filtered_noise = white_noise  # Uproszczone
            
            # Przetwarzanie przez strukturę NOISE BOX
            # Sumator NB81 (wejście + sprzężenie)
            node1 = filtered_noise + params['NBFBK'] * delay_lines[3][delay_indices[3]]
            
            # Pierwsza linia opóźnienia (NBDL1)
            delay_lines[0][delay_indices[0]] = node1
            delayed1 = delay_lines[0][delay_indices[0]]
            
            # Mnożenie przez NCGAIN
            scaled = params['NCGAIN'] * delayed1
            
            # Sumator NB82
            node2 = scaled + delay_lines[1][delay_indices[1]]
            
            # Druga linia opóźnienia (NBDL2)
            delay_lines[1][delay_indices[1]] = node2
            delayed2 = delay_lines[1][delay_indices[1]]
            
            # Trzecia linia opóźnienia (NBDL3)
            delay_lines[2][delay_indices[2]] = delayed2
            delayed3 = delay_lines[2][delay_indices[2]]
            
            # Sumator NB83
            node3 = delayed2 + delayed3
            
            # Limitator szybkości (42)
            limited = self.rate_limiter.process(node3, rate_signal[i], prev_limiter_out)
            prev_limiter_out = limited
            
            # Czwarta linia opóźnienia (NBDL4)
            delay_lines[3][delay_indices[3]] = limited
            delayed4 = delay_lines[3][delay_indices[3]]
            
            # Aktualizacja indeksów opóźnienia
            for j in range(4):
                delay_indices[j] = (delay_indices[j] + 1) % len(delay_lines[j])
            
            # Obwiednia szumu (43)
            envelope = self.env_gen.noise_envelope(i, num_samples, params)
            output[i] = params['NGAIN'] * limited * envelope
            
        return output
    
    def _generate_rate_signal(self, harmonic, params):
        """Generuje sygnał RATE zgodnie z Fig. 10"""
        # Wzmocnienie i ograniczenie (36)
        rate = params['RATE_GAIN'] * harmonic
        rate = np.clip(rate, -1, 1)
        
        # Filtr górnoprzepustowy (37)
        b, a = sig.butter(1, 100, 'highpass', fs=self.sample_rate)
        rate = sig.lfilter(b, a, rate)
        
        # Obcięcie ujemnych wartości (38)
        rate = np.maximum(rate, 0)
        
        # Obwiednia (39) - uproszczona
        envelope = np.ones(len(rate))
        return rate * envelope


class RateLimiter:
    """Limitator szybkości (Fig. 12)"""
    def process(self, input_val, rate_limit, prev_out):
        # Równanie: OUT = prev_out + clip(IN - prev_out, -rate_limit, rate_limit)
        diff = input_val - prev_out
        diff_clipped = np.clip(diff, -rate_limit, rate_limit)
        return prev_out + diff_clipped


class LinearResonator:
    """Rezonator liniowy (Fig. 15)"""
    def __init__(self, sample_rate, buffer_size=2048):
        self.sample_rate = sample_rate
        self.delay_line = np.zeros(buffer_size)
        self.delay_index = 0
        self.filter_state = 0.0  # Stan filtra wszechprzepustowego
        
    def process(self, harmonic_signal, noise_signal, params, num_samples):
        output = np.zeros(num_samples)
        combined_input = harmonic_signal + noise_signal
        
        for i in range(num_samples):
            # Pobierz opóźnioną wartość
            delay_output = self.delay_line[self.delay_index]
            
            # Filtr dolnoprzepustowy (47) - uproszczony
            lp_filtered = 0.99 * delay_output
            
            # Filtr górnoprzepustowy (49) - uproszczony
            hp_filtered = lp_filtered  # W praktyce: hp_filter(lp_filtered)
            
            # Generator obwiedni FBK (50)
            fb_gain = params['FBK']  # Stałe w tej implementacji
            
            # Filtr wszechprzepustowy (52)
            # Równanie: y = a*x + x_prev
            apf_output = 0.7 * hp_filtered + self.filter_state
            self.filter_state = hp_filtered - 0.7 * apf_output
            
            # Sprzężenie zwrotne (53)
            feedback = params['TFBK'] * apf_output
            
            # Sumator wejściowy (46)
            input_sum = combined_input[i] + feedback
            
            # Linia opóźnienia (54)
            self.delay_line[self.delay_index] = input_sum
            
            # Wyjście (13)
            output[i] = delay_output
            
            # Aktualizacja indeksu opóźnienia
            self.delay_index = (self.delay_index + 1) % len(self.delay_line)
            
        return output


class EnvelopeGenerator:
    """Generator obwiedni (Fig. 7, 13)"""
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        
    def attack_sustain_release(self, sample_index, total_samples, params):
        """Obwiednia ADSR dla składowej harmonicznej (Fig. 7)"""
        attack_time = params['attack_time']
        sustain_level = params['sustain_level']
        release_time = params['release_time']
        
        attack_end = int(attack_time * self.sample_rate)
        release_start = total_samples - int(release_time * self.sample_rate)
        
        if sample_index < attack_end:
            return sustain_level * (sample_index / attack_end)
        elif sample_index < release_start:
            return sustain_level
        else:
            release_pos = (sample_index - release_start) / (total_samples - release_start)
            return sustain_level * (1 - release_pos)
    
    def noise_envelope(self, sample_index, total_samples, params):
        """Obwiednia dla szumu (Fig. 13) - uproszczona"""
        # W patentie: stała wartość po krótkim ataku
        attack_time = 0.01 * self.sample_rate
        if sample_index < attack_time:
            return sample_index / attack_time
        return 1.0
    
# Inicjalizacja syntezatora
organ = PhysicalModelOrgan(sample_rate=44100)


sine_params = {
    'CLIP1': 1.0,
    'CLIP2': 1.0,
    'GAIN1': 1.0,
    'GAIN2': 0.0,
    
    'GAIND': 0.0,       # WYŁĄCZENIE nonlin_out (tu siedzi nieliniowość)
    'GAINF': 1.0,       # UŻYJ tylko przepuszczonego filtered_bp (bez distortion)

    'CDEL': 0.0,
    'CBYP': 1.0,
    
    'NGAIN': 0.0,
    'NBFBK': 0.0,
    'NCGAIN': 0.0,
    'RATE_GAIN': 0.0,
    
    'FBK': 0.0,
    'TFBK': 0.0,

    'attack_time': 0.01,
    'sustain_level': 1.0,
    'release_time': 0.01
}


# Generowanie czystego tonu 440 Hz
audio = organ.render_note(440.0, 3.0, params=sine_params)


# Normalizacja i zapis
''' audio = audio / np.max(np.abs(audio)) '''

audio = audio - np.mean(audio)  # usuń przesunięcie stałe

import scipy.io.wavfile as wav
wav.write("example_organ_pipe.wav", 44100, audio.astype(np.float32))