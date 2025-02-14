class IDGenerator:
    '''Klasa bazowa do generowania unikalnych identyfikatorów.

    Klasa ta zapewnia mechanizm generowania unikalnych identyfikatorów dla różnych obiektów.
    Identyfikatory są generowane w sposób automatyczny, aby nie powtarzały się.

    Atrybuty:
        used_ids (set): Zbiór przechowujący użyte identyfikatory.
        counter (int): Licznik, który jest inkrementowany w celu wygenerowania nowego identyfikatora.

    Metody:
        generate_unique_id(): Generuje unikalny identyfikator, który nie powtarza się.
    '''

    def __init__(self):
        self.used_ids = set()
        self.counter = 1

    def generate_unique_id(self):
        '''Generuje unikalny identyfikator.

        Sprawdza, czy identyfikator jest już używany, a jeśli tak, inkrementuje go, aż znajdzie nieużywany identyfikator.

        Zwraca:
            int: Unikalny identyfikator.
        '''

        while self.counter in self.used_ids:
            self.counter +=1
            self.used_ids.add(self.counter)
        return self.counter


class StopIDGenerator(IDGenerator):
    '''Generator unikalnego identyfikatora dla głosu organowego.

    Dziedziczy po klasie IDGenerator i dostosowuje ją do generowania identyfikatorów
    dla głosów organowych.

    Metody:
        generate_unique_id(): Generuje unikalny identyfikator dla głosu organowego.
    '''

    def __init__(self):
        super().__init__()

    def generate_unique_id(self):
        '''Generuje unikalny identyfikator dla głosu organowego.

        Zwraca:
            int: Unikalny identyfikator głosu organowego.
        '''
        return super().generate_unique_id()
    

class DivisionalIDGenerator(IDGenerator):
    '''Generator unikalnego identyfikatora dla sekcji organowej.

    Dziedziczy po klasie IDGenerator i dostosowuje ją do generowania identyfikatorów
    dla sekcji organowych.

    Metody:
        generate_unique_id(): Generuje unikalny identyfikator dla sekcji organowej.
    '''

    def __init__(self):
        super().__init__()

    def generate_unique_id(self):
        '''Generuje unikalny identyfikator dla sekcji organowej.

        Zwraca:
            int: Unikalny identyfikator sekcji organowej.
        '''
        return super().generate_unique_id()


class Divisional:
    '''Reprezentuje sekcję organową, do której należy głos organowy.

    Atrybuty:
        name (str): Nazwa sekcji organowej.
        id (int): Unikalny identyfikator sekcji organowej.
        stops_ids (list): Lista identyfikatorów głosów organowych należących do sekcji organowej.

    Metody:
        add_stop(stop_id): Dodaje identyfikator głosu organowego do sekcji.
    '''

    def __init__(self, name, id_generator: DivisionalIDGenerator):
        self.name = name
        self.id = id_generator.generate_unique_id() # Generuje unikalne id
        self.stops_ids = [] # Lista id głosów

    def add_stop(self, stop_id):
        '''Dodaje identyfikator głosu do sekcji organowej.

        Args:
            stop_id (int): Unikalny identyfikator głosu organowego.
        '''
        self.stops_ids.append(stop_id)
    

class Divisionals:
    '''Reprezentuje sekcję organową, do której należą głosy organowe.

    Atrybuty:
        name (str): Nazwa sekcji organowej (np. Hauptwerk).
        id (int): Unikatowy identyfikator sekcji organowej.
        stop_ids (list[int]): Lista identyfikatorów głosów organowych należących do sekcji organowej.

    Args:
        name (str): Nazwa sekcji organowej.
        id_generator (DivisionalIDGenerator): Generator unikalnego identyfikatora sekcji organowej.

    Metody:
        add_stop_id(stop_id): Dodaje identyfikator głosu organowego do sekcji organowej.
    '''

    def __init__(self, name: str, id_generator):
        self.name = name
        self.id = id_generator.generate_unique_id()
        self.stop_ids = []

    def add_stop_id(self, stop_id: int):
        '''Dodaje identyfikator głosu organowego do sekcji organowej.

        Args:
            stop_id (int): Unikalny identyfikator głosu organowego.
        '''
        self.stop_ids.append(stop_id)


class Stop:
    '''Reprezentuje pojedynczy głos organowy.

    Atrybuty:
        name (str): Nazwa głosu organowego.
        divisional (Divisionals): Obiekt sekcji organowej, do której należy głos organowy.
        id (int): Unikalny identyfikator głosu organowego.
        state (bool | None): Aktualny stan głosu (True = włączony, False = wyłączony, None = nieokreślony).

    Args:
        name (str): Nazwa głosu organowego.
        divisional (Divisionals): Sekcja organowa, do której należy głos.
        id_generator (StopIDGenerator): Generator unikalnego identyfikatora głosu organowego.

    Metody:
        set_on(): Ustawia głos jako włączony.
        set_off(): Ustawia głos jako wyłączony.
        toggle(): Przełącza stan głosu organowego.
        get_state(): Zwraca aktualny stan głosu organowego.
    '''

    def __init__(self, name: str, divisional, id_generator):
        self.name = name
        self.divisional = divisional
        self.id = id_generator.generate_unique_id()
        self.state = None  # None = stan nieokreślony

        # Dodanie ID głosu do sekcji organowej
        self.divisional.add_stop_id(self.id)

    def set_on(self):
        """Ustawia głos organowy jako włączony."""
        self.state = True

    def set_off(self):
        """Ustawia głos organowy jako wyłączony."""
        self.state = False

    def toggle(self):
        """Przełącza stan głosu organowego.

        - Jeśli stan jest None → ustawia na True.
        - Jeśli stan to True/False → zmienia na przeciwny.
        """
        if self.state is None:
            self.set_on()
        else:
            self.state = not self.state

    def get_state(self) -> bool | None:
        '''Zwraca aktualny stan głosu organowego.

        Returns:
            bool | None: Stan głosu (True - włączony, False - wyłączony, None - nieokreślony).
        '''
        return self.state

