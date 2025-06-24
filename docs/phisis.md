# Dokumentacja parametrów syntezy dźwięku organów piszczałkowych

## Wprowadzenie

Niniejsza dokumentacja opisuje parametry używane w implementacji syntezy dźwięku organów piszczałkowych metodą modelowania fizycznego. Dokumentacja pomoże w zrozumieniu wpływu poszczególnych parametrów na brzmienie generowanego dźwięku.
Ścieżka poznawania wpływu parametrów

Aby efektywnie nauczyć się wpływu parametrów na brzmienie, zalecam następującą ścieżkę eksperymentów:

    - Parametry podstawowe (częstotliwość, długość piszczałki)
    - Modulacje i nieliniowości (głębokość modulacji, poziom clippingu)
    - Komponent szumowy (poziom szumu, skala szybkości)
    - Filtracja w rezonatorze (współczynniki filtrów)
    - Obwiednia czasowa (czasy ataku, wybrzmiewania, etc.)
    - Zaawansowane interakcje między parametrami

Dokumentacja parametrów

Parametry podstawowe:

    f0 (Hz) - częstotliwość podstawowa generowanego dźwięku

        - Wpływ: Określa wysokość dźwięku
        - Typowe wartości: 440 Hz (A4), zakres 20-4000 Hz
        - Eksperyment: Zmieniaj o oktawy (podwajaj/haluj wartość)

    pipe_length (m) - długość wirtualnej piszczałki

        - Wpływ: Wpływa na charakterystykę rezonansu
        - Typowe wartości: 0.5-8 m (im dłuższa, tym niższe częstotliwości rezonansowe)
        - Eksperyment: Dostosuj do f0 (dłuższe dla niższych dźwięków)

Parametry modulacji i nieliniowości

    mod_depth (bezwymiarowy) - głębokość modulacji częstotliwości

        - Wpływ: Tworzy naturalne wahania wysokości dźwięku
        - Typowe wartości: 0.001-0.01 (większe = bardziej "żywy" dźwięk)
        - Eksperyment: Zwiększaj stopniowo od 0.001

    lfo_freq (Hz) - częstotliwość modulacji niskoczęstotliwościowej

        - Wpływ: Szybkość wahań wysokości dźwięku
        - Typowe wartości: 2-8 Hz
        - Eksperyment: Testuj z różnymi mod_depth

    nonlinear_gain (bezwymiarowy) - wzmocnienie nieliniowego przetwarzania

        - Wpływ: Wpływa na bogactwo harmoniczne
        - Typowe wartości: 1.5-2.5
        - Eksperyment: Zwiększaj dla bardziej "metalicznego" brzmienia

    clip_level (bezwymiarowy) - poziom ograniczenia amplitudy

        - Wpływ: Wpływa na ostrzejsze przycięcie sygnału
        - Typowe wartości: 0.7-1.0
        - Eksperyment: Zmniejszaj dla bardziej agresywnego brzmienia

Parametry szumu

    noise_level (bezwymiarowy) - poziom komponentu szumowego

        - Wpływ: Dodaje szumy ataku ("chiff") i tło
        - Typowe wartości: 0.01-0.1
        - Eksperyment: Zwiększaj dla bardziej "dmuchanego" brzmienia

    rate_scale (bezwymiarowy) - skala szybkości limitera

        - Wpływ: Kontroluje gwałtowność zmian szumu
        - Typowe wartości: 0.1-0.5
        - Eksperyment: Mniejsze wartości = płynniejsze przejścia

Parametry rezonatora

    lp_coeffs (tablica) - współczynniki filtra dolnoprzepustowego

        - Wpływ: Tłumi wysokie częstotliwości w rezonatorze
        - Typowe wartości: [0.85, -0.15]
        - Eksperyment: Zmieniaj pierwszy współczynnik (0.7-0.95)

    hp_coeffs (tablica) - współczynniki filtra górnoprzepustowego

        - Wpływ: Usuwa składową stałą
        - Typowe wartości: [0.95, -0.95]
        - Eksperyment: Rzadko wymaga zmian

    ap_coeffs (tablica) - współczynniki filtra all-pass

        - Wpływ: Wpływa na charakterystykę fazową
        - Typowe wartości: [0.7, -0.7]
        - Eksperyment: Testuj różne wartości (0.5-0.9)

    tfbk (bezwymiarowy) - współczynnik sprzężenia zwrotnego

        - Wpływ: Siła rezonansu
        - Typowe wartości: 0.6-0.8 (dodatnie dla otwartych, ujemne dla zamkniętych piszczałek)
        - Eksperyment: Zwiększaj dla dłuższego wybrzmiewania

Parametry obwiedni

    attack_time (s) - czas ataku

        - Wpływ: Jak szybko dźwięk osiąga pełną głośność
        - Typowe wartości: 0.05-0.2 s
        - Eksperyment: Krótsze = bardziej perkusyjne brzmienie

    decay_time (s) - czas wybrzmiewania do poziomu sustain

        - Wpływ: Jak szybko dźwięk przechodzi do poziomu podtrzymania
        - Typowe wartości: 0.1-0.3 s
        - Eksperyment: Dłuższe = bardziej płynne przejście

    sustain_level (bezwymiarowy) - poziom podtrzymania

        - Wpływ: Głośność w fazie podtrzymania
        - Typowe wartości: 0.5-0.9
        - Eksperyment: Niższe = bardziej "wokalne" brzmienie

    release_time (s) - czas zanikania

        - Wpływ: Jak szybko dźwięk zanika po zwolnieniu klawisza
        - Typowe wartości: 0.3-1.0 s
        - Eksperyment: Dłuższe = bardziej "kościelne" brzmienie

    noise_attack (s) - czas ataku komponentu szumowego

        - Wpływ: Jak szybko pojawia się szum ataku
        - Typowe wartości: 0.01-0.05 s
        - Eksperyment: Krótsze = bardziej wyraźne "chiff"

Zalecane eksperymenty

    Eksperyment z f0 i pipe_length:

        - Ustaw f0=440, pipe_length=2.5
        - Zmieniaj pipe_length (1.25, 5.0) i obserwuj zmiany w spektrum

    Eksperyment z modulacjami:

        - Ustaw mod_depth=0, lfo_freq=5
        - Stopniowo zwiększaj mod_depth (0.001, 0.005, 0.01)
        - Zmieniaj lfo_freq (2, 5, 10 Hz)

    Eksperyment z szumem:

        - Ustaw noise_level=0.01, rate_scale=0.3
        - Zwiększaj noise_level do 0.1
        - Zmieniaj rate_scale (0.1, 0.5)

    Eksperyment z rezonatorem:

        - Zmieniaj lp_coeffs[0] (0.7, 0.85, 0.95)
        - Testuj różne tfbk (0.5, 0.7, -0.7)

    Eksperyment z obwiednią:

        - Ustaw krótki attack_time (0.05) i długi release_time (1.0)
        - Porównaj z długim attack_time (0.2) i krótkim release_time (0.3)