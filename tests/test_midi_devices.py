import unittest
from unittest.mock import patch
import mido
from core.midi_core import MidiDevices

class TestMidiDevices(unittest.TestCase):
    def test_get_input_devices(self):
        """Testuje, czy get_input_devices zwraca poprawną listę urządzeń wejściowych."""
        devices = MidiDevices()
        excepted_devices = mido.get_input_names()
        actual_devices = devices.get_input_devices()
        self.assertEqual(actual_devices, excepted_devices, "Listy urządzeń są zgodne.")

    def test_get_output_devices(self):
        """Testuje, czy get_output_devices zwraca poprawną listę urządzeń wyjściowych."""
        devices = MidiDevices()
        expected_devices = mido.get_output_names()  # Bezpośrednie wywołanie mido
        actual_devices = devices.get_output_devices()  # Wywołanie metody z klasy
        self.assertEqual(actual_devices, expected_devices, "Listy urządzeń wyjściowych nie są zgodne.")

class TestMidiDevicesNoDevices(unittest.TestCase):
    @patch("mido.get_input_names")
    @patch("mido.get_output_names")
    def test_no_input_devices(self, mock_get_output_names, mock_get_input_names):
        """Testuje zachowanie gdy nie ma dostępnych urządzeń wejściowych"""
        mock_get_input_names.return_value = []
        mock_get_output_names.return_value = ["Virtual Output"]

        devices = MidiDevices()
        with self.assertRaises(ValueError) as context:
            devices.get_input_devices()
        self.assertEqual(str(context.exception), "Nie odnaleziono żadnego wejściowego urządzenia MIDI.")

    @patch("mido.get_input_names")
    @patch("mido.get_output_names")
    def test_no_output_devices(self, mock_get_output_names, mock_get_input_names):
        """Testuje zachowanie gdy nie ma dostępnych urządzeń wyjściowych"""
        mock_get_input_names.return_value = ["Virtual Input"]
        mock_get_output_names.return_value = []

        devices = MidiDevices()
        with self.assertRaises(ValueError) as context:
            devices.get_output_devices()
        self.assertEqual(str(context.exception), "Nie odnaleziono żadnego wyjściowego urządzenia MIDI.")


if __name__ == "__main__":
    unittest.main()