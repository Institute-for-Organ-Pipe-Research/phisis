import mido

class MidiDeviceConfig:
    '''Konfiguruje urządzenia midi'''
    def __init__(self, input_name=None, output_name=None):
        self.MIDI_IN_devices = {}
        self.MIDI_OUT_devices = {}

        self.update_devices()

    def update_devices(self):
        """Aktualizuje listę urządzeń MIDI we wszystkich dostępnych portach wejściowych i wyjściowych."""
        input_devices = mido.get_input_names()
        output_devices = mido.get_output_names()

        self.MIDI_IN_devices = {device: {'connected': False} for device in input_devices}
        self.MIDI_OUT_devices = {device: {'connected': False} for device in output_devices}

    def list_devices(self):
        """Wyświetla dostępne urządzenia wejściowe i wyjściowe."""
        print('Urządzenia wejściowe:')
        for index, (key, value) in enumerate(self.MIDI_IN_devices.items()):
            print(f'[{index}] {key} - connected: {value["connected"]}')

        print('\n\n')

        print('Urządzenia wyjściowe:')
        for index, (key, value) in enumerate(self.MIDI_OUT_devices.items()):
            print(f'[{index}] {key} - connected: {value["connected"]}')

    def get_devices(self):
        """Zwraca słowniki urządzeń wejściowych i wyjściowych."""
        return {'MIDI_IN': self.MIDI_IN_devices, 'MIDI_OUT': self.MIDI_OUT_devices}

    def connect_device(self, devices: list):
        for device in devices:
            if device in self.MIDI_IN_devices:
                self.MIDI_IN_devices[device]['connected': True]
            if device in self.MIDI_OUT_devices:
                self.MIDI_OUT_devices[device]['connected': True]

    def connect_configurator(self):
        """Konfiguruje połączenia urządzeń MIDI na podstawie statusu 'connected'."""
        print('Konfiguracja urządzeń MIDI\n')

        # Sprawdź urządzenia wejściowe (MIDI IN)
        disconnected_in_devices = {
            key: value for key, value in self.MIDI_IN_devices.items()
            if isinstance(value, dict) and not value.get('connected', False)
        }

        if disconnected_in_devices:
            print("Urządzenia wejściowe (MIDI IN):")
            for index, (key, value) in enumerate(disconnected_in_devices.items()):
                print(f"[{index}] {key} - connected: {value['connected']}")
            try:
                input_indices = list(map(int, input("Wybierz urządzenia do połączenia (oddzielone przecinkami): ").split(',')))
                for index in input_indices:
                    key = list(disconnected_in_devices.keys())[index]
                    self.MIDI_IN_devices[key]['connected'] = True
                    print(f"Urządzenie {key} połączone.")
            except (ValueError, IndexError):
                print("Błędny wybór. Spróbuj ponownie.")
                self.connect_configurator()

        # Sprawdź urządzenia wyjściowe (MIDI OUT)
        disconnected_out_devices = {
            key: value for key, value in self.MIDI_OUT_devices.items()
            if isinstance(value, dict) and not value.get('connected', False)
        }

        if disconnected_out_devices:
            print("\nUrządzenia wyjściowe (MIDI OUT):")
            for index, (key, value) in enumerate(disconnected_out_devices.items()):
                print(f"[{index}] {key} - connected: {value['connected']}")
            try:
                output_indices = list(map(int, input("Wybierz urządzenia do połączenia (oddzielone przecinkami): ").split(',')))
                for index in output_indices:
                    key = list(disconnected_out_devices.keys())[index]
                    self.MIDI_OUT_devices[key]['connected'] = True
                    print(f"Urządzenie {key} połączone.")
            except (ValueError, IndexError):
                print("Błędny wybór. Spróbuj ponownie.")
                self.connect_configurator()

