from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
import mido
import sys


def print_midi_devices():
    print('Input devices:')
    for device in mido.get_input_names():
        print(f'  {device}')
    print('Output devices:')
    for device in mido.get_output_names():
        print(f'  {device}')


class PedalLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.button_states = {
            "Untersatz 32'": 0,
            "Contrabass 16'": 1,
            "Subbass 16'": 2,
            "Octavbass 8'": 3,
            "Gedackt 8'": 4,
            "Choralbass 4'": 5,
            "Posaune 32'": 6,
            "Posaune 16'": 7,
            "Trompete 8'": 8
        }
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label = QLabel('Pedal')
        layout.addWidget(label)

        for button_name, program_number in self.button_states.items():
            button = QPushButton(button_name)
            button.setCheckable(True)
            button.toggled.connect(lambda checked, name=button_name, program=program_number: self.send_midi_message(name, program, checked))
            layout.addWidget(button)

        self.setLayout(layout)

    def send_midi_message(self, name, program, checked):
        channel = 4
        state = "Enabled" if checked else "Disabled"
        print(f"{state}: {name}")
        with mido.open_output("loopMIDI Port 0") as midi_out:
            midi_message = mido.Message('program_change', channel=channel, program=program)
            midi_out.send(midi_message)


class HauptwerkLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.UI()

    def UI(self):
        layout = QVBoxLayout()

        # Przypisanie przycisków do odpowiednich wartości programu MIDI
        self.button_states = {
            "Praestant 16'": 9,
            "Principal 8'": 10,
            "Holzflöte 8'": 11,
            "Röhrflöte 8'": 12,
            "Gambe 8'": 13,
            "Octave 4'": 14,
            "Spitzflöte 4'": 15,
            "Quinte 2 2/3'": 16,
            "Octave 2'": 17,
            "Mixtur major 4-5f. 2 2/3'": 18,
            "Mixtur minor 4f. 1 1/3'": 19,
            "Trompete 16'": 20,
            "Trompete 8'": 21
        }

        Hauptwerk = QLabel('Hauptwerk')
        layout.addWidget(Hauptwerk)

        for button_name, program_number in self.button_states.items():
            button = QPushButton(button_name)
            button.setCheckable(True)
            button.toggled.connect(lambda checked, name=button_name, program=program_number: self.send_midi_message(name, program, checked))
            layout.addWidget(button)

        self.setLayout(layout)

    def send_midi_message(self, name, program_number, checked):
        print(f"{'Enabled' if checked else 'Disabled'}: {name}")

        try:
            channel = 4  # Kanał MIDI (zakres 0-15)

            midi_message = mido.Message('program_change', channel=channel, program=program_number)
            print(f"Wysyłanie komunikatu MIDI: {midi_message}")

            with mido.open_output("loopMIDI Port 1") as midi_out:
                midi_out.send(midi_message)
                print("Komunikat MIDI wysłany.")
        except Exception as e:
            print(f"Błąd podczas wysyłania komunikatu MIDI: {e}")


class SchwellwerkLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.UI()

    def UI(self):
        layout = QVBoxLayout()
        self.button_states = {
            "Bourdon 16'": 22,
            "Principal 8'": 23,
            "Nachthorn Gedackt 8'": 24,
            "Corno dolce 8'": 25,
            "Viola 8'": 26,
            "Vox celeste 8'": 27,
            "Geigenprincipal 4'": 28,
            "Querflöte 4'": 29,
            "Nazard 2 2/3'": 30,
            "Flageolett 2'": 31,
            "Tierce 1 3/5'": 32,
            "Larigot 1 1/3'": 33,
            "Plein Jeu 4-5f. 2'": 34,
            "Scharff 4f. 1'": 35,
            "Trompete harmonique 8'": 36,
            "Hautbois 8'": 37,
            "Clairon 4'": 38
        }

        schwellwerk_label = QLabel('Schwellwerk')
        layout.addWidget(schwellwerk_label)

        for button_name, program_number in self.button_states.items():
            button = QPushButton(button_name)
            button.setCheckable(True)
            button.toggled.connect(lambda checked, name=button_name, program=program_number: self.send_midi_message(name, program, checked))
            layout.addWidget(button)

        self.setLayout(layout)

    def send_midi_message(self, name, program_number, checked):
        print(f"{'Enabled' if checked else 'Disabled'}: {name}")

        try:
            channel = 4  # Kanał MIDI (zakres 0-15)

            midi_message = mido.Message('program_change', channel=channel, program=program_number)
            print(f"Wysyłanie komunikatu MIDI: {midi_message}")

            with mido.open_output("loopMIDI Port 1") as midi_out:
                midi_out.send(midi_message)
                print("Komunikat MIDI wysłany.")
        except Exception as e:
            print(f"Błąd podczas wysyłania komunikatu MIDI: {e}")


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
