import os
import sys
from random import randrange

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QAction, QIcon, QTextDocument
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QApplication, QDial, QGridLayout, QHBoxLayout,
                               QLabel, QMainWindow, QPushButton, QTabWidget,
                               QVBoxLayout, QWidget, QFileDialog)

class SecureDial():
    """
    Is same class from Mast.py
    Will be the component for second part of password, with first part being typed
    """
    def __init__(self):
        super().__init__()
        self.r1 = randrange(100)
        self.r2 = randrange(100)

        self.dial = QDial()
        self.dial.setRange(0,99)
        self.dial.setSingleStep(0)
        self.dial.setPageStep(0)
        self.dial.setWrapping(True)
        self.dial.setSliderPosition(self.r1)
        self.v = (self.r1+self.r2)%100
        self.dial.valueChanged.connect(self.dial_value)
        self.mouse_press = False
        self.label = QLabel()
        self.label.setText("****")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.dial)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.label)

        self.dial.sliderPressed.connect(self.d_pressed)
        self.dial.sliderReleased.connect(self.d_released)


    def d_pressed(self):
        self.label.setText(str(self.v))

    def d_released(self):
        self.label.setText("****")

    def dial_value(self, v):
        self.v = (v+self.r2)%100
        self.label.setText(str(self.v))


class SecondaryPassword(QWidget):
    """
    Use SecureDials to create secondary part of inputted password for encryption/decryption
    """
    def __init__(self, num_dials=4):
        super().__init__()

        self.dials = [SecureDial() for _ in range(num_dials)]

        hbox = QHBoxLayout()
        for dial in self.dials:
            hbox.addLayout(dial.layout)
        grid = QGridLayout()
        self.setLayout(hbox)


class WelcomeWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.browser = QWebEngineView()

        s = """
                <html>
                    <head>
                        <style>
                        </style>
                        <body>
                            <h1>Welcome</h1>
                            <p>File Encrypter allows you to encypt and decrypt your files in a more secure way.</p>
                            <p>Simply choose a file and add both a typed password as well as 4 numbers chosen on screen.
                            </p>
                            <h2>Why File Encrypter?</h2>
                            <p>In order to combat keyloggers, both on screen and typed passwords are used to encrypt a file.
                            No passwords are saved, so be careful about forgetting passwords or typing them in wrong!</p>
                        </body>
                    </head>
                </html>
                """
        self.browser.setHtml(s)
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Encrypter")
        self.setFixedSize(QSize(800, 600))
        menu = self.menuBar()

        self.secondary = SecondaryPassword()
        self.welcome = WelcomeWidget()

        self.tabbed = QTabWidget()
        self.tabbed.addTab(self.welcome, "Welcome")
        self.tabbed.addTab(self.secondary, "Secondary Password")
        
        self.tabbed.setDocumentMode(True)
        self.tabbed.setCurrentIndex(0)

        file_menu = menu.addMenu("&File")
        close_button_action = QAction("Close", self)
        close_button_action.triggered.connect(self.clickClose)
        file_menu.addAction(close_button_action)

        self.setCentralWidget(self.tabbed)

    def clickClose(self, s):
        print("Click on Close Button", s)
        self.close()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
