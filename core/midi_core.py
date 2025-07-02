from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
import mido
import threading

class MidiDevices:
    def __init__(self) -> None:
        self.inputDevices = mido.get_input_names()
        self.outportDevices = mido.get_output_names()

    def get_input_devices(self):
        """Zwraca listę dostępnych urządzeń wejściowych MIDI."""
        if not self.inputDevices:
            print(self.inputDevices)
            raise ValueError("Nie odnaleziono żadnego wejściowego urządzenia MIDI.")
        return self.inputDevices

    def get_output_devices(self):
        """Zwraca listę dostępnych urządzeń wyjściowych MIDI."""
        if not self.outportDevices:
            raise ValueError("Nie odnaleziono żadnego wyjściowego urządzenia MIDI.")
        return self.outportDevices


class MidiInput:
    """Klasa do obsługi wejścia MIDI."""
    def __init__(self, port_name):
        self.port = mido.open_input(port_name)

    def read_messages(self):
        """Generator zwracający komunikaty MIDI."""
        for message in self.port:
            yield message


class MidiOutput:
    """Klasa do obsługi wyjścia MIDI."""
    def __init__(self, port_name):
        self.port = mido.open_output(port_name)

    def send_message(self, message):
        """Wysyła komunikat MIDI."""
        self.port.send(message)


class MidiModifier(ABC):
    """Interface dla modyfikatorów MIDI."""
    def __init__(self) -> None:
        self.enable = False

    def enable(self):
        """Włącza modyfikator"""
        self.enable = True

    def disable(self):
        """Włącza modyfikator"""
        self.enable = False

    @abstractmethod
    def modyfy(self, message):
        pass

    @abstractmethod
    def save_state():
        pass

    @abstractmethod
    def load_state():
        pass


class MidiRouter:
    """Klasa zarządzająca przetwarzaniem komunikatów MIDI"""
    def __init__(self, midi_input, midi_output) -> None:
        self.midi_input = midi_input
        self.midi_output = midi_output
        self.modyfiers = []
        self.preset_index = None

        self.load_last_preset()

        self.executor = ThreadPoolExecutor(max_workers=2)
        self.running = False

    def add_modyfier(self, modyfier):
        """Dodaje modyfikator."""
        self.modyfiers.append(modyfier)

    def remove_modyfier(self, modyfier):
        """Usuwa modyfikator."""
        self.modyfiers.remove(modyfier)

    def process_message(self, message):
        """Przetwarza komunikaty MIDI."""
        for modyfier in self.modyfiers:
            if modyfier.enable:
                message = modyfier.modyfy(message)
        return message
        
    def start(self):
        """Uruchamia router MIDI."""
        self.running = True
        self.executor.submit(self._read_messages)
        self.executor.submit(self._send_messages)

    def stop(self):
        """Zatrzymuje router MIDI."""
        self.running = False
        self.executor.shutdown(wait=True) # Doczytać o parametrze wait=True

    def _read_messages(self):
        """Czyta komuikaty MIDI z wejścia."""
        while self.running:
            for message in self.midi_input.read_messages():
                processed_message = self.process_message(message)
                self.midi_output.send_message(processed_message)

    def _send_messages(self):
        """Wysyła przetworzone komunikaty MIDI."""
        while self.running:
            pass # Można dodać dodatkową logikę
    
    def save_last_preset(self):
        pass

    def load_last_preset(self):
        pass
    
    def init_preset(self):
        if True == True:
            pass
        else:
            self.preset_index = 0

    def load_preset(self, state, preset_index):
        pass


if __name__ == "__main__":
    pass