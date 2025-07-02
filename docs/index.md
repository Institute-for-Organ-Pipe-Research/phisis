# Dokumentacja: Badawcza implementacja technologii Viscount Physis (US7442869B2)

## Cel projektu

Celem projektu jest zaimplementowanie fizycznego modelu dźwięku organowego zgodnego z patentem **US7442869B2**, stosowanym m.in. w technologii **Viscount Physis™**. Implementacja ta umożliwia analizę struktury modelu, generowanie tonu organowego oraz eksperymentowanie z parametrami modelu.

> ⚠️ **Uwaga prawna:** Technologia Viscount Physis™ jest objęta ochroną patentową:
>
> * USA Patent: [US7442869B2](https://patents.google.com/patent/US7442869B2/en)
> * Europejski patent: EP1639334B1
> * Właściciel: VISCOUNT INTERNATIONAL S.p.A.
>
> Implementacja ma charakter **naukowo-edukacyjny** i nie służy celom komercyjnym.

---

## Struktura główna

### `PhysicalModelOrgan`

Główna klasa odpowiedzialna za renderowanie dźwięku nuty z wykorzystaniem trzech komponentów:

* `HarmonicGenerator` – komponent bazowy
* `NoiseGenerator` – model generowania szumu
* `LinearResonator` – rezonator i filtracja

Działa na bazie parametrów `params` i domyślnej częstotliwości próbkowania 44100 Hz.

### `default_params()`

Zwraca słownik parametrów zgodny z wartościami domyślnymi opisanymi w patencie. Możliwa jest aktualizacja dowolnego parametru, np. `GAIN1`, `NGAIN`, `TFBK`, `attack_time` itd.

---

## Komponenty syntezy

### `HarmonicGenerator`

Odpowiada za podstawowy sygnał dźwiękowy (oscylator harmoniczny, obwiednia, modulacja amplitudy, linia opóźnienia, filtr BP, funkcja nieliniowa).

### `NoiseGenerator`

Bazuje na strukturze "NOISE BOX" z filtrami dolnoprzepustowymi, losową modulacją i limitatorem prędkości zmian.

### `LinearResonator`

Implementuje rezonator akustyczny zgodny z rysunkiem Fig. 15 z patentu. Zawiera filtr dolno- i górnoprzepustowy, filtr wszechprzepustowy i linię opóźnienia z regulowanym sprzężeniem zwrotnym.

### `EnvelopeGenerator`

Obwiednia typu ADSR dla harmonicznych i oddzielna dla szumu.

### `LowFrequencyOscillator`

Wewnętrzny LFO (modulacja amplitudy i częstotliwości).

### `FrequencyModulator`

Dodaje subtelną losową modulację częstotliwości na poziomie cyklu.

### `RateLimiter`

Ogranicza prędkość zmian sygnału (dla szumu) zgodnie z Fig. 12.

---

## Przykładowe użycie

```python
if __name__ == "__main__":
    organ = PhysicalModelOrgan(sample_rate=44100)
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
    audio = organ.render_note(440.0, 3.0, params=sine_params)
    wav.write("output/organ_pipe.wav", 44100, (audio * 32767).astype(np.int16))
```

---

## Wymagania

* Python 3.8+
* NumPy
* SciPy

```bash
pip install numpy scipy
```

---

## Planowane rozszerzenia

* Interfejs użytkownika do eksploracji parametrów
* Uczenie maszynowe doboru parametrów na podstawie dostarczonej próbki dźwięku oczyszczonej z pogłosu
* Symulacja strojenia i przestrzennego rozmieszczenia piszczałek

---

## Licencja

Projekt edukacyjny. Brak powiązań z producentem Viscount. 
