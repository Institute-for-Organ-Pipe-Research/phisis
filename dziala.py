import sys
from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

class HoverEventFilter(QObject):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Enter or event.type() == QEvent.HoverEnter:
            self.callback(f'Hover przycisku {watched.text()}')
            return True
        elif event.type() == QEvent.Leave or event.type() == QEvent.HoverLeave:
            self.callback(f'Opuszczono przycisk {watched.text()}')
            return True
        return super().eventFilter(watched, event)

class GUI(QWidget):
    def __init__(self):
        super().__init__()

        button1 = QPushButton('Przycisk 1')
        button2 = QPushButton('Przycisk 2')

        layout = QVBoxLayout(self)
        layout.addWidget(button1)
        layout.addWidget(button2)

        button1.clicked.connect(lambda: self.debug_push_button('1'))
        button2.clicked.connect(lambda: self.debug_push_button('2'))

        self.filter = HoverEventFilter(self.debug_hover_button)  # Przechowywanie filtra jako atrybutu klasy

        button1.installEventFilter(self.filter)
        button2.installEventFilter(self.filter)

        button1.setAttribute(Qt.WA_Hover, True)
        button2.setAttribute(Qt.WA_Hover, True)

    def debug_push_button(self, txt):
        print(f'Kliknięto przycisk {txt}')

    def debug_hover_button(self, txt):
        print(txt)

app = QApplication(sys.argv)
gui = GUI()
gui.show()
sys.exit(app.exec())
