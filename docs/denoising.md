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

## Narzędzie: Organ Pipe Denoiser (Tools)

Narzędzie to służy do przygotowania próbek dźwiękowych piszczałek organowych do uczenia maszynowego, zwłaszcza do doboru parametrów syntezy fizycznej zgodnie z patentem.

### Funkcje narzędzia:

- Redukcja pogłosu (reverb reduction) z oryginalnych nagrań A0 i R0-R3
- Generowanie syntetycznego ogona R na podstawie fazy sustain próbki A0 lub jako filtrowany szum (sucha akustyka)
- Łączenie próbek z crossfade w celu zachowania naturalności brzmienia
- GUI do wyboru folderów, próbek i ustawień parametrów
- Przetwarzanie wsadowe wielu próbek

### Wymagania:

- Python 3.8+
- Biblioteki: numpy, scipy, soundfile, tkinter

### Instalacja bibliotek:

```bash
pip install numpy scipy soundfile
