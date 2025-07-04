---
title: Oscylator cyfrowy
mathjax: true
---

# Dokumentacja do symulacji i wizualizacji oscylatorów sinusoidalnych i zmian częstotliwości (blok nr 9)

## Cel skryptu

Skrypt demonstruje zachowanie sygnałów sinusoidalnych w różnych scenariuszach częstotliwościowych — stałej częstotliwości, liniowej modulacji częstotliwości (chirp), skoków częstotliwości z i bez artefaktów cyfrowych. Celem jest pokazanie problemów stabilności i jakości dźwięku w cyfrowych oscylatorach oraz przedstawienie rozwiązania opatentowanego stabilizującego amplitudę podczas nagłych zmian częstotliwości.

---

## Spis treści

1. [Stała częstotliwość (Wykres 1)](#1-stała-częstotliwość-wykres-1)
2. [Liniowy chirp częstotliwości (Wykres 2)](#2-liniowy-chirp-częstotliwości-wykres-2)
3. [Zoom: Początek i koniec chirpa (2b i 2c)](#2b-i-2c-zoom-na-początek-i-koniec-chirpa)
4. [Skok częstotliwości z artefaktem (Wykres 3)](#3-skok-częstotliwości-ze-sztucznym-artefaktem-wykres-3)
5. [Skok bez artefaktu — opatentowane rozwiązanie (Wykres 4)](#4-skok-częstotliwości-bez-artefaktu--opatentowane-rozwiązanie-wykres-4)
6. [Widmo harmoniczne sygnałów (4c)](#4c-widmo-harmoniczne-sygnałów-przy-skoku-częstotliwości)
7. [Porównanie widm globalnych (Wykres 5)](#5-porównanie-widm-globalnych)
8. [Szczegóły implementacyjne oscylatora](#szczegóły-implementacyjne-oscylatora-opatentowanego)
9. [Podsumowanie](#podsumowanie)
10. [Źródła](#źródła-i-inspiracje)

---

## 1. Stała częstotliwość (Wykres 1)

- **Co jest pokazane:**  
  Klasyczna sinusoidalna fala o częstotliwości $f = 440 \,\mathrm{Hz}$ (ton a' z muzyki) generowana na cztery pełne okresy.

- **Matematyka:**  

  $$
  x(t) = \sin(2\pi f t), \quad f = 440\,\mathrm{Hz}, \quad t \in \left[0, \frac{4}{f}\right]
  $$

- **Cel:**  
  Pokazanie idealnej, stabilnej sinusoidy bez modulacji.

---

## 2. Liniowy chirp częstotliwości (Wykres 2)

- **Co jest pokazane:**  
  Sinusoida o częstotliwości zmieniającej się liniowo w czasie od $f_0 = 200\, \mathrm{Hz}$ do $f_1 = 1000\, \mathrm{Hz}$ w czasie $T = 0.015\, \mathrm{s}$.

- **Matematyka:**  

  $$f(t) = f_0 + k t, \quad k = \frac{f_1 - f_0}{T}$$

  $$
  \varphi(t) = 2\pi \int_0^t f(\tau)\,d\tau = 2\pi \left(f_0 t + \frac{1}{2} k t^2\right)
  $$

  $$
  x(t) = \sin(\varphi(t))
  $$

- **Cel:**  
  Pokazanie efektu modulacji częstotliwości (FM) w czasie rzeczywistym.

---

## 2b i 2c. Zoom na początek i koniec chirpa

- **Co jest pokazane:**  
  Szczegółowy widok fali w zakresie niskich i wysokich częstotliwości.

---

## 3. Skok częstotliwości ze sztucznym artefaktem (Wykres 3)

- **Co jest pokazane:**  
  Sygnał sinusoidalny, w którym częstotliwość skacze nagle z 330 Hz do 550 Hz, co powoduje niestabilność amplitudy.

- **Opis problemu:**  
  Klasyczne oscylatory cyfrowe nie kompensują zmiany fazy, przez co pojawiają się zakłócenia.

---

## 4. Skok częstotliwości bez artefaktu — opatentowane rozwiązanie (Wykres 4)

- **Co jest pokazane:**  
  Porównanie dwóch sygnałów:  
  - z artefaktem (klasyczny)  
  - bez artefaktu (z algorytmem patentowym)

- **Opis algorytmu:**

  Stabilizacja amplitudy podczas zmiany częstotliwości za pomocą wzmacniania zmiennej stanu i ograniczania amplitudy.

- **Algorytm:**

  $$
  \begin{aligned}
  \mathrm{VAR1}_{n} &= \mathrm{VAR1}_{n-1} - F^2 \cdot \mathrm{VAR2}_{n-1} \\
  \mathrm{VAR2}_{n} &= \mathrm{VAR2}_{n-1} \cdot (1 + \varepsilon) + \mathrm{VAR1}_{n}
  \end{aligned}
  $$

  $$
  \mathrm{VAR1} = \mathrm{clip}(\mathrm{VAR1}, -1, 1)
  $$

  $$
  F = 2 \sin\left(\frac{\pi f}{f_s}\right)
  $$

---

## 4c. Widmo harmoniczne sygnałów przy skoku częstotliwości

- **Opis:**  
  Analiza amplitudowa (logarytmiczna) fragmentu sygnału, obliczona za pomocą FFT.

---

## 5. Porównanie widm globalnych

- **Opis:**  
  Widmo pełnego sygnału potwierdza stabilność wersji patentowej.

---

## Szczegóły implementacyjne oscylatora opatentowanego

Oscylator generuje sinusoidy poprzez dwie zmienne stanu i iteracyjne aktualizacje. Zapewnia stabilność amplitudy nawet przy skokowych zmianach częstotliwości.

- $f$ — bieżąca częstotliwość  
- $f_s$ — częstotliwość próbkowania  
- $\varepsilon \approx 0.001$ — czynnik wzmacniający energię

---

## Podsumowanie

- Klasyczne oscylatory mogą powodować rozstrajanie i zanikanie sygnału.
- Chirp pozwala analizować ciągłą modulację $f(t)$.
- Skoki częstotliwości wprowadzają artefakty.
- Opatentowany oscylator cyfrowy eliminuje te artefakty, stabilizując amplitudę.
- Widmo sygnału potwierdza skuteczność metody.

---

## Źródła i inspiracje

- [Patent US7442869B2](https://patents.google.com/patent/US7442869B2/en) – *Digital oscillator with amplitude stabilization*
