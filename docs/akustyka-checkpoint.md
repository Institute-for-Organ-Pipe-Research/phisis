# Dokumentacja: Symulacja Organów w Przestrzeni 3D

## Wprowadzenie

Projekt symulacji organów w przestrzeni 3D pozwala na odwzorowanie kierunkowości dźwięku na podstawie pozycji sekcji organowych i położenia słuchacza. Model uwzględnia efekt ITD (Interaural Time Difference - międzyskrzelowa różnica czasu) i ILD (Interaural Level Difference - międzyskrzelowa różnica poziomu dźwięku) dla realistycznej percepcji przestrzennej.

## Struktura Modelu

1. Klasa Pipe

Reprezentuje pojedynczą piszczałkę w sekcji organowej.

Atrybuty:

pitch: Częstotliwość dźwięku (Hz).

position: Pozycja w ramach sekcji organowej (nie w przestrzeni 3D).

2. Klasa OrganSection

Reprezentuje sekcję organową, w której znajdują się piszczałki.

Atrybuty:

name: Nazwa sekcji (np. Swell, Great).

position: Pozycja sekcji w przestrzeni 3D.

pipes: Lista piszczałek w sekcji.

Metody:

add_pipe(pitch): Dodaje piszczałkę o podanej częstotliwości.

arrange_pipes(arrangement_type): Rozmieszcza piszczałki w sekcji w sposób liniowy, zbieżny lub rozbieżny.

3. Klasa SoundSource3D

Reprezentuje źródło dźwięku w przestrzeni 3D.

Atrybuty:

position: Pozycja źródła dźwięku w przestrzeni.

Metody:

compute_itd(listener_position): Oblicza ITD na podstawie odległości do lewego i prawego ucha.

compute_ild(listener_position): Oblicza ILD na podstawie odległości do słuchacza.

4. Klasa SoundSimulation3D

Symuluje propagację dźwięku i jego percepcję przez słuchacza.

Atrybuty:

listener_position: Pozycja słuchacza w przestrzeni 3D.

sounds: Lista źródeł dźwięku.

Metody:

add_sound_source(position): Dodaje źródło dźwięku do symulacji.

simulate_sound(sound_wave, sample_rate): Symuluje odbiór dźwięku przez oba uszy, uwzględniając ITD i ILD.

Proces Symulacji

Tworzymy instancję SoundSimulation3D.

Definiujemy sekcje organowe (OrganSection) i ich pozycje.

Dodajemy piszczałki do sekcji i rozmieszczamy je w ramach sekcji.

Każda sekcja zostaje dodana jako źródło dźwięku w symulacji.

Generujemy falę dźwiękową (np. sinusoidalną) i przetwarzamy ją z uwzględnieniem ITD i ILD.

Finalne sygnały dla lewego i prawego ucha mogą zostać przesłane do systemu audio.