# FileEncrypter

## Use Case
File Encrypter is a standalone application for securing your files. Keyloggers are a serious security risk, as they can record your inputted passwords and be used to break into your files later. FileEncrypter works with two passwords, one typed, and one chosen on the screen, to help limit the damage keyloggers can do. Either choose a password you can remember, or save it to your keychain/locker. Currently only developed for MacOS. With another developer on the Windows System it can be expanded to work there, but without proper testing there is no way of knowing if the encrypting and decrypting process will actually work. 

## Running

To run this file, clone the repo
```bash
git clone https://github.com/aajmorgan6/FileEncrypter
```

(Optional) Set up a virtual environment and activate it
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install all necessary libraries
```bash
pip3 install -r requirements.txt
```

Run the program
```bash
python3 gui.py
```

## GUI (PySide6)
The PySide6 library was used to create the user interface. There are two main tabs, Encrypt and Decrypt, with the main differences being two password fields used in Encrypt and a button to load the password in Decrypt for a specific file. 

The Secure Dials are created in the `class SecureDial()` which gives their functionality, including the label being hidden when not pressed and setting up a random first number and a random start to the list of numbers. These can be looped through and created in the `EncryptWidget` and `DecryptWidget` classes. These numbers provide the "salt" used in the encryption, which is explained more below.

PySide6 also allows for `Dialogs`, which are the popups created at certain points in the app. The `QMessageDialog` is used the most, with information about the keychain, status of decryption, and more. `QFileDialog` is the file chooser dialog which launches when the "Choose File" button is clicked on either EncryptWidget or DecryptWidget. For the EncryptWidget, any file can be chosen and the encryption process with delete the old file and output a `FILENAME.*.box` file. DecryptWidget can only take in `*.box` files to be decrypted, and will delete the .box file and output the original file. 


# Behind the scenes

### Encryption
Looking at `encrypt.py`, you can see all the functions used to encrypt and decrypt files. The main library is `cryptography`, and I use the Fernet submodule. Normally, Fernet can generate a key and save it to your device in a file like `key.key`, however, that would not allow other people to decrypt the files sent to them that were encrypted on another device.

Instead, we can use cryptography's `Scrypt` class to generate a key from a password
```python3
kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
derived = kdf.derive(password.encode())
```
and then encode that using the `base64` module.

The salt used in Scrypt is the onscreen input provided by the user, giving extra protection to the files as it can be any number 4 - 8 digits long.

### Keychain/Locker Access

Some of the passwords that may be used on this can be overwhelmingly long depending on the user, so saving the typed password as well as the numbers from the 4 dials can be safer.
With a simple command run through the `keyring` module, the program get set, get, and delete passwords from the Keychain or Locker, and allow only FileEncrypter to access the password.

Apple Keychain is already password protected and secure, so saving file passwords there (or Locker for Windows) is secure for you but easily accessable. 
Sometimes files can be decrypted and then encrypted again. If you want to use a new Keychain password, the program will overwrite the old password and use the new password.


# Pyinstaller

Since this has a GUI aspect to it, the library `pyinstaller` can be used to create an application out of this so Python commands won't have to be run to launch and it can be in the hotbar. It is mostly set up with the `fileencrypter.ico` and `FileEncrypter.spec` files, so only a couple steps have to be taken.

First,
```bash
pip3 install pyinstaller
```
and then run (from the same directory as before)
```bash
pyinstaller FileEncrypter.spec
```
This will create a `build` folder and a `dist` folder. The `dist` folder will have the FileEncrypter application that can be moved to `Applications`. `build` will include the `FileEncrypter.pkg` file that can be used do download the application as well.

# Future Steps
As stated before, a Windows machine would allow development to be spread to the Windows environment, but without testing it has not been updated to use on Windows. The frontend could also use some work, as it is bare bones on the GUI for the most part, especially the Welcome Page, but that is more outside of my skill set and would involve a lot of work and research, especially getting into HTML and CSS and the layout functionalities of PySide6.
