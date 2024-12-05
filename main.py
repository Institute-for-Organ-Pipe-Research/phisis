from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
import mido
import sys
from voices import PEDAL_VOICES, HAUPTWERK_VOICES, SCHWELLWERK_VOICES


def print_midi_devices():
    print('Input devices:')
    for device in mido.get_input_names():
        print(f'  {device}')
    print('Output devices:')
    for device in mido.get_output_names():
        print(f'  {device}')


class MidiLayout(QWidget):
    def __init__(self, layout_name, button_states):
        super().__init__()
        self.layout_name = layout_name
        self.button_states = button_states
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label = QLabel(self.layout_name)
        layout.addWidget(label)

        for button_name, program_number in self.button_states.items():
            button = QPushButton(button_name)
            button.setCheckable(True)
            button.toggled.connect(lambda checked, name=button_name, program=program_number: self.send_midi_message(name, program, checked))
            layout.addWidget(button)

        self.setLayout(layout)

    def send_midi_message(self, name, program_number, checked):
        channel = 4  # Kanał MIDI (zakres 0-15)
        state = "Enabled" if checked else "Disabled"
        print(f"{state}: {name}")

        try:
            midi_message = mido.Message('program_change', channel=channel, program=program_number)
            with mido.open_output("loopMIDI Port 1") as midi_out:
                midi_out.send(midi_message)
                print(f"Wysyłanie komunikatu MIDI: {midi_message}")
        except Exception as e:
            print(f"Błąd podczas wysyłania komunikatu MIDI: {e}")


class PedalLayout(MidiLayout):
    def __init__(self):
        super().__init__("Pedal", PEDAL_VOICES)


class HauptwerkLayout(MidiLayout):
    def __init__(self):
        super().__init__("Hauptwerk", HAUPTWERK_VOICES)


class SchwellwerkLayout(MidiLayout):
    def __init__(self):
        super().__init__("Schwellwerk", SCHWELLWERK_VOICES)


class AppLayout(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.addWidget(PedalLayout())
        layout.addWidget(HauptwerkLayout())
        layout.addWidget(SchwellwerkLayout())
        self.setLayout(layout)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-midi-devices":
        print_midi_devices()

    app = QApplication(sys.argv)
    print_midi_devices()
    window = AppLayout()
    window.show()
    sys.exit(app.exec())
