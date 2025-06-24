
# Opis algorytmu syntezy dźwięku organowego (na podstawie US7442869B2)

## Cel algorytmu
Celem patentu jest realistyczna **synteza dźwięku piszczałki organowej** na podstawie modelu fizycznego (ang. *Physis synthesis*), w tym zjawisk akustycznych w obrębie:
- generatora (język, ustnik, źródło energii),
- ciała piszczałki (rezonator),
- modulacji dźwięku,
- oraz szumów i nieliniowości.

---

## Struktura modelu według patentu (schemat z Fig. 15)

+-----------------------------+
      | Harmonic Component Generator| <-- sinusoida z modulacją
      +-----------------------------+
                  |
                  v
      +-----------------------------+
      | Random (Aleatory) Component | <-- generuje szum
      +-----------------------------+
                  |
                  v
             +----------+
             | Resonator| <-- filtracja, opóźnienie, odbicie fazy
             +----------+
                  |
                  v
             +----------+
             | Envelope |
             +----------+
                  |
                  v
             Final Output

---
## Matematyka implementacji

### 1. Generacja komponentu harmonicznego

$$
x[n] = \alpha \cdot x[n-1] - x[n-2]
$$

gdzie:

- $f_0$ – częstotliwość podstawowa,
- $f_{\text{lfo}}$ – częstotliwość modulacji LFO,
- $d$ – głębokość modulacji,
- $f(t) = f_0 \cdot (1 + d \cdot \sin(2\pi f_{\text{lfo}} t) + \text{noise})$,
- $\alpha = 2\cos\left(2\pi \frac{f(t)}{f_s}\right)$.

Dodatkowo sygnał jest delikatnie wzmacniany i przycinany:

$$
x[n] \leftarrow \min(\max(1.001 \cdot x[n], -\text{clip}), \text{clip})
$$

---

### 2. Komponent szumowy (Random Component Generator)

Algorytm bazuje na ograniczonej zmianie różnicy wartości RNG:

$$
\text{output}[n] = \text{output}[n-1] + \min(\max(R[n] - R[n-1], -r[n]), r[n])
$$

gdzie:
- $R[n]$ – wartość losowa z rozkładu jednostajnego,
- $r[n]$ – dynamiczna szybkość zmiany, zależna od harmonicznej.

---

### 3. Nieliniowe przekształcenie

Wzmocnienie i zniekształcenie harmonicznego sygnału:

$$
y[n] = \text{gain} \cdot x[n]^2 - 1
$$

---

### 4. Rezonator

Modeluje propagację fali w piszczałce z uwzględnieniem:

- filtr dolnoprzepustowy (LP),
- filtr górnoprzepustowy (HP),
- filtr all-pass (AP),
- linia opóźniająca (delay line),
- sprzężenie zwrotne (feedback `tfbk`).

#### Filtry:

$$
\begin{aligned}
\text{LP}[n] &= a_0 \cdot \text{in}[n] + a_1 \cdot \text{LP}[n-1] \\
\text{HP}[n] &= b_0 \cdot \text{LP}[n] + b_1 \cdot \text{HP}[n-1] \\
\text{AP}[n] &= c_0 \cdot \text{HP}[n] + c_1 \cdot \text{AP}[n-1]
\end{aligned}
$$

#### Linia opóźniająca i sprzężenie zwrotne:

$$
\text{delay}[n] = \text{AP}[n] \cdot \text{tfbk}
$$

Faza sygnału jest odwracana zależnie od typu piszczałki (otwarta/zamknięta) przez `tfbk < 0`.

---

### 5. Obwiednia (ADSR)

Wzorzec dynamiczny:

1. Attack: $0 \to 1$ przez czas `attack_time`
2. Decay: $1 \to sustain$ przez `decay_time`
3. Sustain: stała wartość `sustain_level`
4. Release: $sustain \to 0$ przez `release_time`

---

## ⚖️ Porównanie implementacji vs patent

| Część modelu                     | Opis wg patentu                  | Obecna implementacja            |
|----------------------------------|----------------------------------|----------------------------------|
| Harmonic Generator              | Oscylator z LFO + losowość       | ✅ obecny w `generate_harmonic` |
| Random Component Generator      | Szum ograniczany sygnałem sterującym | ✅ obecny w `generate_noise`  |
| Nieliniowość                    | Zniekształcenie przez nieliniowe przekształcenie | ✅ `nonlinear_gain` i clip  |
|
# Opis algorytmu syntezy dźwięku organowego (na podstawie US7442869B2)

## Cel algorytmu
Celem patentu jest realistyczna **synteza dźwięku piszczałki organowej** na podstawie modelu fizycznego (ang. *Physis synthesis*), w tym zjawisk akustycznych w obrębie:
- generatora (język, ustnik, źródło energii),
- ciała piszczałki (rezonator),
- modulacji dźwięku,
- oraz szumów i nieliniowości.

---

## Struktura modelu według patentu (schemat z Fig. 15)

+-----------------------------+
      | Harmonic Component Generator| <-- sinusoida z modulacją
      +-----------------------------+
                  |
                  v
      +-----------------------------+
      | Random (Aleatory) Component | <-- generuje szum
      +-----------------------------+
                  |
                  v
             +----------+
             | Resonator| <-- filtracja, opóźnienie, odbicie fazy
             +----------+
                  |
                  v
             +----------+
             | Envelope |
             +----------+
                  |
                  v
             Final Output

---
## Matematyka implementacji

### 1. Generacja komponentu harmonicznego

$$
x[n] = \alpha \cdot x[n-1] - x[n-2]
$$

gdzie:

- $f_0$ – częstotliwość podstawowa,
- $f_{\text{lfo}}$ – częstotliwość modulacji LFO,
- $d$ – głębokość modulacji,
- $f(t) = f_0 \cdot (1 + d \cdot \sin(2\pi f_{\text{lfo}} t) + \text{noise})$,
- $\alpha = 2\cos\left(2\pi \frac{f(t)}{f_s}\right)$.

Dodatkowo sygnał jest delikatnie wzmacniany i przycinany:

$$
x[n] \leftarrow \min(\max(1.001 \cdot x[n], -\text{clip}), \text{clip})
$$

---

### 2. Komponent szumowy (Random Component Generator)

Algorytm bazuje na ograniczonej zmianie różnicy wartości RNG:

$$
\text{output}[n] = \text{output}[n-1] + \min(\max(R[n] - R[n-1], -r[n]), r[n])
$$

gdzie:
- $R[n]$ – wartość losowa z rozkładu jednostajnego,
- $r[n]$ – dynamiczna szybkość zmiany, zależna od harmonicznej.

---

### 3. Nieliniowe przekształcenie

Wzmocnienie i zniekształcenie harmonicznego sygnału:

$$
y[n] = \text{gain} \cdot x[n]^2 - 1
$$

---

### 4. Rezonator

Modeluje propagację fali w piszczałce z uwzględnieniem:

- filtr dolnoprzepustowy (LP),
- filtr górnoprzepustowy (HP),
- filtr all-pass (AP),
- linia opóźniająca (delay line),
- sprzężenie zwrotne (feedback `tfbk`).

#### Filtry:

$$
\begin{aligned}
\text{LP}[n] &= a_0 \cdot \text{in}[n] + a_1 \cdot \text{LP}[n-1] \\
\text{HP}[n] &= b_0 \cdot \text{LP}[n] + b_1 \cdot \text{HP}[n-1] \\
\text{AP}[n] &= c_0 \cdot \text{HP}[n] + c_1 \cdot \text{AP}[n-1]
\end{aligned}
$$

#### Linia opóźniająca i sprzężenie zwrotne:

$$
\text{delay}[n] = \text{AP}[n] \cdot \text{tfbk}
$$

Faza sygnału jest odwracana zależnie od typu piszczałki (otwarta/zamknięta) przez `tfbk < 0`.

---

### 5. Obwiednia (ADSR)

Wzorzec dynamiczny:

1. Attack: $0 \to 1$ przez czas `attack_time`
2. Decay: $1 \to sustain$ przez `decay_time`
3. Sustain: stała wartość `sustain_level`
4. Release: $sustain \to 0$ przez `release_time`

---

## ⚖️ Porównanie implementacji vs patent

| Część modelu                     | Opis wg patentu                  | Obecna implementacja            |
|----------------------------------|----------------------------------|----------------------------------|
| Harmonic Generator              | Oscylator z LFO + losowość       | ✅ obecny w `generate_harmonic` |
| Random Component Generator      | Szum ograniczany sygnałem sterującym | ✅ obecny w `generate_noise`  |
| Nieliniowość                    | Zniekształcenie przez nieliniowe przekształcenie | ✅ `nonlinear_gain` i clip  |
| Rezonator                       | LP, HP, AP + delay line + tfbk   | ✅ `resonator`                  |
| Anharmoniczność                 | All-pass dla przesunięć fazy     | 🔶 uproszczony, ręczne `ap_coeffs` |
| Faza (open vs stopped)          | Sterowane przez `tfbk`           | ✅ `tfbk` obecne                 |
| Emisja z różnych punktów        | Top vs mouth                     | ❌ brak                         |
| Sprzężenie generator ↔ rezonator| W realu silne, w patencie słabe  | ✅ niezależne w implementacji    |
| Obwiednia ADSR                  | Wygenerowana programowo          | ✅ `generate_envelope`          |

---

## 🔧 Możliwe ulepszenia

1. Automatyczne dobieranie `ap_coeffs` dla *anharmoniczności*.
2. Złożony delay z podziałem na mouth/top output.
3. Użycie konwolucji w miejscu filtrów IIR dla precyzji.
4. Dynamiczne sterowanie `tfbk` zależnie od tonu. Rezonator                       | LP, HP, AP + delay line + tfbk   | ✅ `resonator`                  |
| Anharmoniczność                 | All-pass dla przesunięć fazy     | 🔶 uproszczony, ręczne `ap_coeffs` |
| Faza (open vs stopped)          | Sterowane przez `tfbk`           | ✅ `tfbk` obecne                 |
| Emisja z różnych punktów        | Top vs mouth                     | ❌ brak                         |
| Sprzężenie generator ↔ rezonator| W realu silne, w patencie słabe  | ✅ niezależne w implementacji    |
| Obwiednia ADSR                  | Wygenerowana programowo          | ✅ `generate_envelope`          |

---

## 🔧 Możliwe ulepszenia

1. Automatyczne dobieranie `ap_coeffs` dla *anharmoniczności*.
2. Złożony delay z podziałem na mouth/top output.
3. Użycie konwolucji w miejscu filtrów IIR dla precyzji.
4. Dynamiczne sterowanie `tfbk` zależnie od tonu.

Jest to projekt z pozostałościami routera midi GrandBridge. Obecnie rozwój skupia się na syntezie phisis zgodnego z https://patents.google.com/patent/US7442869B2/en
- [Parametry phisis](/docs/phisis.md)
 
