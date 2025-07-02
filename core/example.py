import numpy as np
import scipy.signal as sig
import scipy.io.wavfile as wav

class PhysicalModelOrgan:
    """Implementacja patentu US7442869B2 z uzupełnionymi elementami"""
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.harmonic_gen = HarmonicGenerator(sample_rate)
        self.noise_gen = NoiseGenerator(sample_rate)
        self.resonator = LinearResonator(sample_rate)
        self.params = self.default_params()
    
    def default_params(self):
        """Parametry zgodne z patentem z dodatkowymi ustawieniami"""
        return {
            # Generator harmoniczny
            'CLIP1': 0.7, 'CLIP2': 0.5, 'GAIN1': 1.0, 'GAIN2': 0.8,
            'GAIND': 0.6, 'GAINF': 0.4, 'CDEL': 0.3, 'CBYP': 0.7,
            'X0': 0.1, 'Y0': 0.05,  # Parametry nieliniowej funkcji
            'MOD_AMPL': 0.1,  # Głębokość modulacji amplitudy
            
            # Generator szumu
            'NGAIN': 0.5, 'NBFBK': 0.4, 'NCGAIN': 0.6,
            'RATE_GAIN': 1.2, 'NOISE_ATTACK': 0.01,
            
            # Rezonator
            'FBK': 0.85, 'TFBK': 1.0, 'RESONATOR_ATTACK': 0.05,
            
            # Obwiednie
            'attack_time': 0.1, 'decay_time': 0.05, 'sustain_level': 0.8,
            'release_time': 0.3, 'initial_level': 0.0
        }
    
    def render_note(self, freq, duration, params=None):
        """Renderuje nutę z pełną ścieżką sygnału"""
        if params is None:
            params = self.params
        
        num_samples = int(duration * self.sample_rate)
        
        # Generacja składowych
        harmonic = self.harmonic_gen.generate(freq, num_samples, params)
        noise = self.noise_gen.generate(harmonic, num_samples, params)
        output = self.resonator.process(harmonic, noise, params, num_samples)
        
        # Normalizacja i usunięcie składowej stałej
        output = output - np.mean(output)
        return output / np.max(np.abs(output))


class HarmonicGenerator:
    """Generator składowej harmonicznej z pełną implementacją"""
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.osc = HarmonicOscillator(sample_rate)
        self.env_gen = EnvelopeGenerator(sample_rate)
        self.freq_modulator = FrequencyModulator(sample_rate)
        self.lfo = LowFrequencyOscillator(sample_rate)
        
    def generate(self, freq, num_samples, params):
        output = np.zeros(num_samples)
        delay_line = np.zeros(1024)
        delay_index = 0
        
        for i in range(num_samples):
            # Modulacja częstotliwości
            mod_freq = self.freq_modulator.process(freq, self.osc.var1)
            
            # Generacja sygnałów LFO
            lfo_amp, lfo_freq = self.lfo.process()
            
            # Generacja sinusoidy z modulacją
            sin_wave = self.osc.process(mod_freq, params)
            
            # Generacja podwójnej częstotliwości
            double_freq = 2 * sin_wave**2 - 1
            
            # Ścieżka 1
            path1 = sin_wave * params['GAIN1']
            path1 = np.clip(path1, -params['CLIP1'], params['CLIP1'])
            
            # Ścieżka 2
            path2 = double_freq * params['GAIN2']
            path2 = np.clip(path2, -params['CLIP2'], params['CLIP2'])
            
            # Obwiednie
            env = self.env_gen.attack_sustain_release(i, num_samples, params)
            path1 *= env
            path2 *= env
            
            # Sumowanie i modulacja amplitudy
            sum_node = path1 + path2
            modulated = sum_node * (1 + params['MOD_AMPL'] * lfo_amp)
            
            # Linia opóźnienia
            delayed = delay_line[delay_index]
            filtered = params['CBYP'] * modulated + params['CDEL'] * delayed
            
            # Nieliniowa funkcja
            nonlin_out = (filtered + params['X0']) - (filtered + params['X0'])**4 + params['Y0']
            
            # Filtr pasmowoprzepustowy
            if i == 0:  # Inicjalizacja filtra tylko raz
                self.bp_b, self.bp_a = sig.butter(2, [0.9*freq, 1.1*freq], 
                                                 btype='bandpass', 
                                                 fs=self.sample_rate)
            filtered_bp = sig.lfilter(self.bp_b, self.bp_a, [nonlin_out])[0]
            
            # Sumator końcowy
            output[i] = params['GAIND'] * nonlin_out + params['GAINF'] * filtered_bp
            
            # Aktualizacja linii opóźnienia
            delay_line[delay_index] = modulated
            delay_index = (delay_index + 1) % len(delay_line)
            
        return output


class HarmonicOscillator:
    """Oscylator harmoniczny z modulacją"""
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.var1 = 1.0
        self.var2 = 0.0
        
    def process(self, freq, params):
        epsilon = params.get('epsilon', 1e-5)
        F = 2 * np.sin(np.pi * freq / self.sample_rate)
        
        self.var1 = self.var1 - F**2 * self.var2
        self.var2 = self.var2 * (1 + epsilon)
        self.var2 = self.var1 + self.var2
        self.var1 = np.clip(self.var1, -1, 1)
        
        return self.var1


class FrequencyModulator:
    """Modulator częstotliwości zgodnie z Fig. 5-6"""
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.random_pitch = 1.0
        self.last_var1 = 0
        
    def process(self, base_freq, current_var1):
        if self.last_var1 < 0 and current_var1 >= 0:
            self.random_pitch = np.random.uniform(0.98, 1.02)  # ±2% wariacji
        self.last_var1 = current_var1
        return base_freq * self.random_pitch


class LowFrequencyOscillator:
    """LFO dla modulacji amplitudy i częstotliwości"""
    def __init__(self, sample_rate, freq=0.5, ampl=0.1, offset=0.0):
        self.sample_rate = sample_rate
        self.phase = 0
        self.freq = freq
        self.ampl = ampl
        self.offset = offset
        
    def process(self):
        self.phase += 2 * np.pi * self.freq / self.sample_rate
        self.phase %= 2 * np.pi
        
        # Sygnał trójkątny dla modulacji amplitudy
        triangle = 2 * np.abs(self.phase / np.pi - 1) - 1
        output_amp = self.offset + self.ampl * triangle
        
        # Sygnał paraboliczny dla modulacji częstotliwości
        if self.phase < np.pi:
            parabola = 2 * (self.phase/np.pi)**2 - 1
        else:
            parabola = 1 - 2 * ((self.phase-np.pi)/np.pi)**2
        output_freq = parabola
        
        return output_amp, output_freq


class NoiseGenerator:
    """Generator szumu z pełną implementacją Fig. 10-12"""
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.rate_limiter = RateLimiter()
        self.env_gen = EnvelopeGenerator(sample_rate)
        
    def generate(self, harmonic_signal, num_samples, params):
        rate_signal = self._generate_rate_signal(harmonic_signal, params)
        
        # Inicjalizacja NOISE BOX
        delay_lines = [np.zeros(100) for _ in range(4)]
        delay_indices = [0, 0, 0, 0]
        prev_limiter_out = 0.0
        
        output = np.zeros(num_samples)
        
        for i in range(num_samples):
            # Generacja białego szumu
            white_noise = np.random.uniform(-1, 1)
            
            # Filtracja dolnoprzepustowa
            if i == 0:
                self.lp_b, self.lp_a = sig.butter(2, 2000, 'lowpass', fs=self.sample_rate)
            filtered_noise = sig.lfilter(self.lp_b, self.lp_a, [white_noise])[0]
            
            # Przetwarzanie przez NOISE BOX
            node1 = filtered_noise + params['NBFBK'] * delay_lines[3][delay_indices[3]]
            
            delay_lines[0][delay_indices[0]] = node1
            delayed1 = delay_lines[0][delay_indices[0]]
            
            scaled = params['NCGAIN'] * delayed1
            
            node2 = scaled + delay_lines[1][delay_indices[1]]
            delay_lines[1][delay_indices[1]] = node2
            delayed2 = delay_lines[1][delay_indices[1]]
            
            delay_lines[2][delay_indices[2]] = delayed2
            delayed3 = delay_lines[2][delay_indices[2]]
            
            node3 = delayed2 + delayed3
            
            # Limitator szybkości
            limited = self.rate_limiter.process(node3, rate_signal[i], prev_limiter_out)
            prev_limiter_out = limited
            
            delay_lines[3][delay_indices[3]] = limited
            delayed4 = delay_lines[3][delay_indices[3]]
            
            # Aktualizacja indeksów
            for j in range(4):
                delay_indices[j] = (delay_indices[j] + 1) % len(delay_lines[j])
            
            # Obwiednia szumu
            envelope = self.env_gen.noise_envelope(i, num_samples, params)
            output[i] = params['NGAIN'] * limited * envelope
            
        return output
    
    def _generate_rate_signal(self, harmonic, params):
        """Generuje sygnał RATE zgodnie z Fig. 10"""
        rate = params['RATE_GAIN'] * harmonic
        rate = np.clip(rate, -1, 1)
        
        # Filtr górnoprzepustowy
        b, a = sig.butter(1, 100, 'highpass', fs=self.sample_rate)
        rate = sig.lfilter(b, a, rate)
        
        # Obcięcie ujemnych wartości
        rate = np.maximum(rate, 0)
        
        # Obwiednia
        attack_samples = int(params['NOISE_ATTACK'] * self.sample_rate)
        envelope = np.ones(len(rate))
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        return rate * envelope


class RateLimiter:
    """Limitator szybkości zgodnie z Fig. 12"""
    def process(self, input_val, rate_limit, prev_out):
        diff = input_val - prev_out
        diff_clipped = np.clip(diff, -rate_limit, rate_limit)
        return prev_out + diff_clipped


class LinearResonator:
    """Rezonator liniowy z pełną implementacją Fig. 15"""
    def __init__(self, sample_rate, buffer_size=2048):
        self.sample_rate = sample_rate
        self.delay_line = np.zeros(buffer_size)
        self.delay_index = 0
        self.filter_state = np.zeros(2)
        self.apf_state = np.zeros(2)
        
    def process(self, harmonic_signal, noise_signal, params, num_samples):
        output = np.zeros(num_samples)
        combined_input = harmonic_signal + noise_signal
        
        # Inicjalizacja filtrów
        self.lp_b, self.lp_a = sig.butter(2, 4000, 'lowpass', fs=self.sample_rate)
        self.hp_b, self.hp_a = sig.butter(2, 50, 'highpass', fs=self.sample_rate)
        
        for i in range(num_samples):
            # Pobierz opóźnioną wartość
            delay_output = self.delay_line[self.delay_index]
            
            # Filtr dolnoprzepustowy
            lp_filtered = sig.lfilter(self.lp_b, self.lp_a, [delay_output])[0]
            
            # Filtr górnoprzepustowy
            hp_filtered = sig.lfilter(self.hp_b, self.hp_a, [lp_filtered])[0]
            
            # Obwiednia sprzężenia zwrotnego
            if i < params['RESONATOR_ATTACK'] * self.sample_rate:
                fb_gain = params['FBK'] * 1.2  # Wzmocnione sprzężenie podczas ataku
            else:
                fb_gain = params['FBK']
            
            # Filtr wszechprzepustowy
            apf_output = 0.7 * hp_filtered + self.apf_state[0]
            self.apf_state[0] = hp_filtered - 0.7 * apf_output
            
            # Sprzężenie zwrotne
            feedback = params['TFBK'] * apf_output * fb_gain
            
            # Sumator wejściowy
            input_sum = combined_input[i] + feedback
            
            # Linia opóźnienia
            self.delay_line[self.delay_index] = input_sum
            
            # Wyjście
            output[i] = delay_output
            
            # Aktualizacja indeksu
            self.delay_index = (self.delay_index + 1) % len(self.delay_line)
            
        return output


class EnvelopeGenerator:
    """Generator obwiedni z pełną implementacją Fig. 7, 13-14"""
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        
    def attack_sustain_release(self, sample_index, total_samples, params):
        """Obwiednia ADSR dla składowej harmonicznej"""
        attack_time = params['attack_time']
        decay_time = params['decay_time']
        sustain_level = params['sustain_level']
        release_time = params['release_time']
        initial_level = params['initial_level']
        
        attack_end = int(attack_time * self.sample_rate)
        decay_end = attack_end + int(decay_time * self.sample_rate)
        release_start = total_samples - int(release_time * self.sample_rate)
        
        if sample_index < attack_end:
            return initial_level + (1.0 - initial_level) * (sample_index / attack_end)
        elif sample_index < decay_end:
            decay_pos = (sample_index - attack_end) / (decay_end - attack_end)
            return 1.0 - (1.0 - sustain_level) * decay_pos
        elif sample_index < release_start:
            return sustain_level
        else:
            release_pos = (sample_index - release_start) / (total_samples - release_start)
            return sustain_level * (1 - release_pos)
    
    def noise_envelope(self, sample_index, total_samples, params):
        """Obwiednia dla szumu zgodna z Fig. 13"""
        attack_time = params['NOISE_ATTACK']
        if sample_index < attack_time * self.sample_rate:
            return sample_index / (attack_time * self.sample_rate)
        return 1.0


# Przykład użycia
if __name__ == "__main__":
    # Inicjalizacja syntezatora
    organ = PhysicalModelOrgan(sample_rate=44100)
    
    # Parametry dla czystego tonu
    sine_params = organ.default_params()
    sine_params.update({
        'CLIP1': 1.0, 'CLIP2': 1.0,
        'GAIN1': 1.0, 'GAIN2': 0.0,
        'GAIND': 0.0, 'GAINF': 1.0,
        'CDEL': 0.0, 'CBYP': 1.0,
        'NGAIN': 0.0, 'FBK': 0.0, 'TFBK': 0.0,
        'attack_time': 0.01, 'release_time': 0.01,
        'sustain_level': 1.0
    })
    
    # Generowanie i zapis dźwięku
    audio = organ.render_note(440.0, 3.0, params=sine_params)
    wav.write("organ_pipe.wav", 44100, (audio * 32767).astype(np.int16))