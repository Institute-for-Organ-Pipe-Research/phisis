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
        self.UI()

    def UI(self):
        layout = QVBoxLayout()
        self.button_states = {
            "Untersatz 32'": False,
            "Contrabass 16'": False,
            "Subbass 16'": False,
            "Octavbass 8'": False,
            "Gedackt 8'": False,
            "Choralbass 4'": False,
            "Posaune 32'": False,
            "Posaune 16'": False,
            "Trompete 8'": False
        }

        pedal_label = QLabel('Pedal')
        layout.addWidget(pedal_label)

        for button_name in self.button_states.keys():
            button = QPushButton(button_name)
            button.setCheckable(True)
            button.toggled.connect(lambda checked, name=button_name: self.send_midi_message(name, checked))
            layout.addWidget(button)

        self.setLayout(layout)

    def send_midi_message(self, name, checked):
        print(f"{'Enabled' if checked else 'Disabled'}: {name}")


class HauptwerkLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.UI()

    def UI(self):
        layout = QVBoxLayout()
        self.button_states = {
            "Praestant 16'": False,
            "Principal 8'": False,
            "Holzflöte 8'": False,
            "Röhrflöte 8'": False,
            "Gambe 8'": False,
            "Octave 4'": False,
            "Spitzflöte 4'": False,
            "Quinte 2 2/3'": False,
            "Octave 2'": False,
            "Mixtur major 4-5f. 2 2/3'": False,
            "Mixtur minor 4f. 1 1/3'": False,
            "Trompete 16'": False,
            "Trompete 8'": False
        }

        hauptwerk_label = QLabel('Hauptwerk')
        layout.addWidget(hauptwerk_label)

        for button_name in self.button_states.keys():
            button = QPushButton(button_name)
            button.setCheckable(True)
            button.toggled.connect(lambda checked, name=button_name: self.send_midi_message(name, checked))
            layout.addWidget(button)

        self.setLayout(layout)

    def send_midi_message(self, name, checked):
        print(f"{'Enabled' if checked else 'Disabled'}: {name}")


class SchwellwerkLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.UI()

    def UI(self):
        layout = QVBoxLayout()
        self.button_state = {
            "Bourdon 16'": False,
            "Principal 8'": False,
            "Nachthorn Gedackt 8'": False,
            "Corno dolce 8'": False,
            "Viola 8'": False,
            "Vox celeste 8'": False,
            "Geigenprincipal 4'": False,
            "Querflöte 4'": False,
            "Nazard 2 2/3'": False,
            "Flageolett 2'": False,
            "Tierce 1 3/5'": False,
            "Larigot 1 1/3'": False,
            "Plein Jeu 4-5f. 2'": False,
            "Scharff 4f. 1'": False,
            "Trompete harmonique 8'": False,
            "Hautbois 8'": False,
            "Clairon 4'": False
        }

        schwellwerk_label = QLabel('Schwellwerk')
        layout.addWidget(schwellwerk_label)

        for button_name in self.button_state.keys():
            button = QPushButton(button_name)
            button.setCheckable(True)
            button.toggled.connect(lambda checked, name=button_name: self.send_midi_message(name, checked))
            layout.addWidget(button)

        self.setLayout(layout)

    def send_midi_message(self, name, checked):
        print(f"{'Enabled' if checked else 'Disabled'}: {name}")


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
    window = AppLayout()
    window.show()
    sys.exit(app.exec())
