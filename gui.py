import sys
import pathlib
from random import randrange
import touchid #type: ignore

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QApplication, QDial, QGridLayout, QHBoxLayout,
                               QLabel, QMainWindow, QPushButton, QTabWidget,
                               QVBoxLayout, QWidget, QFileDialog, QLineEdit, QMessageBox)

from encrypt import make_key, encrypt_file_algo, decrypt_file_algo, write_secret_string, read_secret_string, delete_keychain

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


class EncryptWidget(QWidget):
    """
    Window to choose file, enter typed password, and then enter on screen password.
    Will then change the specific file to something (*.txt.box?) and remove unencrypted file.
    """
    def __init__(self, num_dials=4):
        super().__init__()
        layout = QGridLayout()

        row_1 = QHBoxLayout()
        self.file_button = QPushButton("Choose File")
        self.file_button.clicked.connect(self.launchDialog)
        row_1.addWidget(self.file_button)
        self.file_label = QLabel()
        row_1.addWidget(self.file_label)

        row_2 = QHBoxLayout()
        self.pass_1_label = QLabel()
        self.pass_1_label.setText("Enter Password: ")
        row_2.addWidget(self.pass_1_label)
        self.pass_1 = QLineEdit()
        self.pass_1.setEchoMode(QLineEdit.Password)
        row_2.addWidget(self.pass_1)
        self.pass_2_label = QLabel()
        self.pass_2_label.setText("Renter Password: ")
        row_2.addWidget(self.pass_2_label)
        self.pass_2 = QLineEdit()
        self.pass_2.setEchoMode(QLineEdit.Password)
        row_2.addWidget(self.pass_2)
        self.pass_match = QLabel()
        row_2.addWidget(self.pass_match)

        self.num_dials = num_dials
        self.dials = [SecureDial() for _ in range(self.num_dials)]

        row_3 = QHBoxLayout()
        for dial in self.dials:
            row_3.addLayout(dial.layout)

        row_4 = QHBoxLayout()
        self.encrypt_button = QPushButton("Encrypt")
        self.encrypt_button.clicked.connect(self.runEncryption)
        row_4.addWidget(self.encrypt_button)

        layout.addLayout(row_1, 1, 1, 1, 1)
        layout.addLayout(row_2, 2, 1, 1, 1)
        layout.addLayout(row_3, 3, 1, 1, 1)
        layout.addLayout(row_4, 4, 1, 1, 1)
        self.setLayout(layout)

    def launchDialog(self):
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select a File",
        )
        self.file_label.setText(str(response[0]))
        self.file_path = pathlib.Path(str(response[0]))
        self.file_path_str = str(response[0])

    def runEncryption(self):
        if self.pass_1.text() != self.pass_2.text():
            dlg = QMessageBox(self)
            dlg.setIcon(QMessageBox.Warning)
            dlg.setText("Passwords don't match")
            dlg.setStandardButtons(QMessageBox.Ok)
            dlg.exec()
        else:
            value = int("".join([str(dial.v) for dial in self.dials]))
            key = make_key(bytes(value), self.pass_1.text())
            encrypt_file_algo(self.file_path_str, key)

            dlg = QMessageBox(self)
            dlg.setWindowTitle("Successfully Encrypted File")
            dlg.setText("Successfully Encrypted File")
            dlg.setStandardButtons(QMessageBox.Ok)
            dlg.exec()

            # clear things up
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Sucessfully Encrypted File")
            dlg.setText("Would you like to save password to keychain?")
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            button = dlg.exec()

            if button == QMessageBox.Yes:
                # Save to keychain?
                success = read_secret_string(self.file_path.name)

                if success:
                    dlg = QMessageBox(self)
                    dlg.setText("File name already saved in keychain.")
                    dlg.setInformativeText("Would you like to overwrite?")
                    dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    result = dlg.exec()

                    if result == QMessageBox.Yes:
                        delete_keychain(self.file_path.name)
                
                write_secret_string(self.file_path.name, f"{self.pass_1.text()},{value}")
                
            self.pass_1.clear()
            self.pass_2.clear()
            self.file_label.setText("")
            # reset dials so next user can't use same presets
            for dial in self.dials:
                dial.r1 = randrange(100)
                dial.r2 = randrange(100)
                dial.dial.setSliderPosition(dial.r1)
                dial.v = (dial.r1+dial.r2)%100
                dial.label.setText("****")


class DecryptWidget(QWidget):

    def __init__(self, num_dials=4):
        super().__init__()
        layout = QGridLayout()
        self.key = None

        row_1 = QHBoxLayout()
        self.file_button = QPushButton("Choose File")
        self.file_button.clicked.connect(self.launchDialog)
        row_1.addWidget(self.file_button)
        self.file_label = QLabel()
        row_1.addWidget(self.file_label)

        row_2 = QHBoxLayout()
        self.pass_1_label = QLabel()
        self.pass_1_label.setText("Enter Password: ")
        row_2.addWidget(self.pass_1_label)
        self.pass_1 = QLineEdit()
        self.pass_1.setEchoMode(QLineEdit.Password)
        row_2.addWidget(self.pass_1)
        self.load_key_btn = QPushButton("Load Password")
        self.load_key_btn.clicked.connect(self.loadKey)
        row_2.addWidget(self.load_key_btn)

        self.num_dials = num_dials
        self.dials = [SecureDial() for _ in range(self.num_dials)]

        row_3 = QHBoxLayout()
        for dial in self.dials:
            row_3.addLayout(dial.layout)

        row_4 = QHBoxLayout()
        self.encrypt_button = QPushButton("Decrypt")
        self.encrypt_button.clicked.connect(self.runDecryption)
        row_4.addWidget(self.encrypt_button)

        layout.addLayout(row_1, 1, 1, 1, 1)
        layout.addLayout(row_2, 2, 1, 1, 1)
        layout.addLayout(row_3, 3, 1, 1, 1)
        layout.addLayout(row_4, 4, 1, 1, 1)
        self.setLayout(layout)

    def launchDialog(self):
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select a File", 
            filter="Box files (*.box)"
        )
        self.file_label.setText(str(response[0]))
        self.file_path = pathlib.Path(str(response[0]))
        self.file_path_str = str(response[0])

    def loadKey(self):
        if self.file_label == "":
            dlg = QMessageBox(self)
            dlg.setWindowTitle("No File Selected")
            dlg.setText("Please select a file to decrypt first.")
            dlg.setStandardButtons(QMessageBox.Ok)
            button = dlg.exec()
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Loading Password")
            dlg.setText(f"Would you like to load password for {self.file_path.name}?")
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            button = dlg.exec()

            if button == QMessageBox.Yes:
                # Save to keychain?
                if touchid.is_available():
                    try:
                        success = touchid.authenticate(reason="authenticate via Touch ID")
                        if success:
                            stored = read_secret_string(self.file_path.name[:-len(".box")])
                            info = stored.split(",")
                            password, value = ",".join(info[:-1]), info[-1]
                            self.key = make_key(bytes(int(value)), password)
                            self.runDecryption()
                    except Exception as e:
                        dlg = QMessageBox(self)
                        dlg.setWindowTitle("Invalid Password")
                        dlg.setText("Invalid Touch ID password")
                        dlg.setStandardButtons(QMessageBox.Ok)
                        dlg.setIcon(QMessageBox.Warning)
                        dlg.exec()

    def runDecryption(self):
        if not self.key:
            value = int("".join([str(dial.v) for dial in self.dials]))
            self.key = make_key(bytes(value), self.pass_1.text())
        success = decrypt_file_algo(self.file_path_str, self.key)
        if not success:
            dlg = QMessageBox(self)
            dlg.setIcon(QMessageBox.Warning)
            dlg.setText("Unable to Decrypt File")
            dlg.setStandardButtons(QMessageBox.Ok)
            dlg.exec()
        else:
            dlg = QMessageBox(self)
            dlg.setText("Successfully Decrypted File")
            dlg.setStandardButtons(QMessageBox.Ok)
            dlg.exec()

        self.file_label.setText("")

        # clear things up
        self.pass_1.clear()
        self.file_label.setText("")
        # reset dials so next user can't use same presets
        for dial in self.dials:
            dial.r1 = randrange(100)
            dial.r2 = randrange(100)
            dial.dial.setSliderPosition(dial.r1)
            dial.v = (dial.r1+dial.r2)%100
            dial.label.setText("****")


class WelcomeWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.browser = QWebEngineView()

        s = """
                <html>
                    <head>
                        <style>
                        </style>
                        <body style="padding: 20px; text-align: center">
                            <h1 style="text-align: center;">Welcome to FileEncrypter</h1>
                            <p>File Encrypter allows you to encypt and decrypt your files in a more secure way.</p>
                            <p>Simply choose a file and add both a typed password as well as 4 numbers chosen on screen.
                            </p>
                            <h2 style="text-align: center; margin-top: 30px">Why FileEncrypter?</h2>
                            <p>In order to combat keyloggers, both on screen and typed passwords are used to encrypt a file.</p>
                            <p>No passwords are saved, so be careful about forgetting passwords or typing them in wrong!</p>
                            <h2 style="text-align: center; margin-top: 30px">Using the Keychain</h2>
                            <p>Sometimes the best passwords are the hardest to remember, especially when you add in the extra numbers involved.</p>
                            <p>If you want, save your password to the Apple Keychain for secure storage.</p>
                            <p>If you are reencrypting a file, you will have the option to overwrite a previously saved password for your new one, but be careful, as that old password will be lost!</p>
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

        self.encrypt = EncryptWidget()
        self.welcome = WelcomeWidget()
        self.decrypt = DecryptWidget()

        self.tabbed = QTabWidget()
        self.tabbed.addTab(self.welcome, "Welcome")
        self.tabbed.addTab(self.encrypt, "Encrypt")
        self.tabbed.addTab(self.decrypt, "Decrypt")
        
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
