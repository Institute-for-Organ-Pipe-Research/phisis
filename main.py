import PySide6.QtCore
from mido import Message
import mido
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
import sys

def print_midi_devices():
        print('Input devices:')
        print(mido.get_input_names())
        print('Output devices:')
        print(mido.get_output_names())


class PedalLayout(QWidget):
    def __init__(self):
        super().__init__()
        # self.midi_out = mido.open_output('Your MIDI Output Port')
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

        Pedal = QLabel('Pedal')
        layout.addWidget(Pedal)

        for button_name in self.button_states.keys():
            button = QPushButton(button_name)
            button.setCheckable(True)
            button.toggled.connect(lambda checked, name=button_name: self.send_midi_message(name, checked))
            layout.addWidget(button)

        self.setLayout(layout)

    def send_midi_message(self, name, checked):
       pass
       # midi_message = mido.Message('program_change', channel=4, program=program_number)


class HauptwerkLayout(QVBoxLayout):
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

        Hauptwerk = QLabel('Hauptwerk')
        layout.addWidget(Hauptwerk)

        for button_name in self.button_states.keys():
            button = QPushButton(button_name)
            button.setCheckable(True)
            button.toggled.connect(lambda checked, name=button_name: self.send_midi_message(name, checked))
            layout.addWidget(button)

        self.setLayout(layout)

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
            "Clairon 4'": False,
        }

        Schwellwerk = QLabel('Schwellwerk')
        layout.addWidget(Schwellwerk)

        for button_name in self.button_states.keys():
            button = QPushButton(button_name)
            button.setCheckable(True)
            button.toggled.connect(lambda checked, name=button_name: self.send_midi_message(name, checked))
            layout.addWidget(button)

        self.setLayout(layout)

class AppLayout(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        layout.addLayout(PedalLayout())
        layout.addLayout(HauptwerkLayout())
        layout.addLayout(SchwellwerkLayout())

        self.setLayout(layout)


if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) > 1 and sys.argv[1] == "-midi-devices" or "midi-devices":
        print_midi_devices()

    app = QApplication([])
    window = AppLayout()
    window.show()
    app.exec()