# Algorytm

```

───────────────────────────────────────────────────────────────────────
 ALGORYTM SYNTEZY ORGANOWEJ - WIZUALIZACJA TEKSTOWA (US7442869B2)
───────────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────────┐
│                        GENERATOR HARMONICZNY (Fig. 3)               │
└─────────────────────────────────────────────────────────────────────┘
                         ↓
               ┌───────────────────┐
               │ Oscylator (Fig. 4) │
               └───────────────────┘
               VAR1[n] = CLIP(VAR1[n-1] - F²·VAR2[n-1], [-1,1]  (29,32)
               VAR2[n] = (VAR2[n-1]·(1+ε)) + VAR1[n]      (30-31)
               F = 2·sin(π·f/fs)                          (definicja)
                         ↓
               ┌───────────────────┐
               │ Nieliniowy blok (15) │
               └───────────────────┘
               y[n] = 2·(VAR1[n])² - 1 = -cos(2ω₀n)       (transformacja)
                         ↓
       ┌────────────────┴─────────────────┐
       │ Ścieżka 1            Ścieżka 2  │
       │ GAIN1·x[n]           GAIN2·y[n]  │ (18a,18b)
       │ CLIP(±CLIP1)         CLIP(±CLIP2)│ (19a,19b)
       │ ENV1[n]              ENV2[n]     │ (20a,20b)
       └───────┬────────────────┬─────────┘
               ↓
         ┌─────────────┐
         │ Sumator (21) │ → z[n] = path1 + path2
         └─────────────┘
               ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     PRZETWARZANIE HARMONICZNE                       │
└─────────────────────────────────────────────────────────────────────┘
         ┌─────────────┐    ┌─────────────┐
         │ Linia opóź. │ → │ CBYP + CDEL·z⁻ᴺ │ (24,25)
         └─────────────┘    └─────────────┘
               ↓
         ┌─────────────┐
         │ Nielin. f(x)│ → f(x) ≈ x - x⁴ (26)
         └─────────────┘
               ↓
   ┌───────────────────────────────┐
   │ Filtr pasmowoprzepustowy (27) │ → H(z) = 1/(1 - r·cos(ω₀)·z⁻¹ + r²·z⁻²)
   └───────────────────────────────┘
               ↓
   ┌───────────────────────────────┐
   │ Sumator wyjściowy (28)        │ → out = GAIND·x + GAINF·BPF(x)
   └───────────────────────────────┘

───────────────────────────────────────────────────────────────────────
┌─────────────────────────────────────────────────────────────────────┐
│                      GENERATOR SZUMU (Fig. 10-12)                   │
└─────────────────────────────────────────────────────────────────────┘
                         ↓
               ┌───────────────────┐
               │ Generator RATE     │
               └───────────────────┘
               RATE[n] = RTGAIN·CLIP(HPF(VAR1[n]))·ENV[n] (Fig. 10)
                         ↓
               ┌───────────────────┐
               │ NOISE BOX (Fig. 11)│ → Struktura z 4 liniami opóźnienia:
               └───────────────────┘   y[n] = Σ (NCGAIN·x[n-k] + NBFBK·y[n-M])
                         ↓
               ┌───────────────────┐
               │ Limitator szybkości│ → y[n] = y[n-1] + CLIP(x[n]-y[n-1], ±RATE[n])
               └───────────────────┘ (Fig. 12)
                         ↓
               ┌───────────────────┐
               │ Mnożenie przez ENV │ → NOISE[n] = NGAIN·y[n]·ENV_NOISE[n]
               └───────────────────┘ (43)

───────────────────────────────────────────────────────────────────────
┌─────────────────────────────────────────────────────────────────────┐
│                      REZONATOR LINIOWY (Fig. 15)                    │
└─────────────────────────────────────────────────────────────────────┘
   ┌───────────────────────┐    ┌───────────────────────┐
   │ Wejście harmoniczne   │    │ Wejście szumowe       │
   └───────────┬───────────┘    └───────────┬───────────┘
               ↓                            ↓
         ┌─────────────┐              ┌─────────────┐
         │ Sumator (46)│ → x[n] = HARMONIC[n] + NOISE[n]
         └─────────────┘
               ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         PĘTLA REZONANSA                             │
└─────────────────────────────────────────────────────────────────────┘
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ Filtr LP (47)│ → │ Filtr HP (49)│ → │ Filtr AP (52)│ → H_AP(z) = (a + z⁻¹)/(1 + a·z⁻¹)
   └─────────────┘    └─────────────┘    └─────────────┘
               ↑            ↓                    ↓
               │    ┌─────────────┐    ┌─────────────┐
               └───┤ Mnożenie FBK │ ←─┤ Mnożenie TFBK│ (53)
                   └─────────────┘    └─────────────┘
                         ↓
                   ┌─────────────┐
                   │ Linia opóź. │ → D(z) = z⁻ᴺ (54)
                   └─────────────┘

───────────────────────────────────────────────────────────────────────
┌─────────────────────────────────────────────────────────────────────┐
│                         WYJŚCIE (13)                               │
└─────────────────────────────────────────────────────────────────────┘
                         ↓
               ┌───────────────────┐
               │ Sygnał wyjściowy  │ → y[n] = TFBK·delay_line[k]
               └───────────────────┘

───────────────────────────────────────────────────────────────────────
 LEGENDA:
 • VAR1, VAR2 - zmienne stanu oscylatora
 • F - współczynnik częstotliwości
 • ε - mała stała stabilizująca (≈1e-5)
 • ω₀ = 2π·f/fs - znormalizowana częstotliwość
 • CLIP(x,a,b) - ograniczenie x do przedziału [a,b]
 • HPF/LPF/APF - filtry: górno-, dolno- i wszechprzepustowy
 • z⁻ᴺ - opóźnienie o N próbek
───────────────────────────────────────────────────────────────────────
```

## Opis

```
Kluczowe elementy zgodne z patentem:

    Struktura systemu (Fig. 2):

        Generator składowej harmonicznej (9)

        Generator składowej losowej (11)

        Rezonator liniowy (12)

    Generator harmoniczny (Fig. 3):

        Oscylator sinusoidalny (14) z równaniami (29)-(32)

        Nieliniowy konwerter częstotliwości (15)

        Ścieżki przetwarzania z ogranicznikami (19a, 19b)

        Obwiednie amplitudy (20a, 20b)

        Linia opóźnienia (24) i filtr (25)

        Nieliniowa funkcja (26)

        Filtr pasmowoprzepustowy (27)

        Sumator wyjściowy (28)

    Generator szumu (Fig. 10-12):

        Generacja sygnału RATE (Fig. 10)

        Struktura NOISE BOX z czterema liniami opóźnienia (Fig. 11)

        Limitator szybkości (42) z implementacją równań (Fig. 12)

    Rezonator liniowy (Fig. 15):

        Filtr dolnoprzepustowy (47)

        Filtr górnoprzepustowy (49)

        Generator obwiedni sprzężenia (50)

        Filtr wszechprzepustowy (52)

        Linia opóźnienia (54)

        Sprzężenie zwrotne (53)

    Obwiednie:

        5-segmentowa obwiednia harmoniczna (Fig. 7)

        Prosta obwiednia szumu (Fig. 13)

```

