# FileEncrypter

## Use Case
File Encrypter is a standalone application for securing your files. It works with two passwords, one typed, and one chosen on the screen, to help limit the damage keyloggers can do. Either choose a password you can remember, or save it to your keychain/locker.

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
pip install -r requirements.txt
```

Run the program
```bash
python gui.py
```

## GUI (PySide6)
The PySide6 library was used to create the user interface. There are two main tabs, Encrypt and Decrypt, with the main differences being two password fields used in Encrypt and a button to load the password in Decrypt for a specific file. 

## Behind the scenes

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
With a simple command run through 
```python3 
subprocess.run(arg_list)
```
a terminal command can be executed to add, find, or delete a password from the keychain. Windows users utilize the `keyring` module for the same things.

Apple Keychain is already password protected and secure, so saving file passwords there (or Locker for Windows) is secure for you but easily accessable. 
Sometimes files can be decrypted and then encrypted again. If you want to use a new Keychain password, the program will overwrite the old password and use the new password.

(MAC ONLY) If you want to find a password you may have forgotten without decrypting your file, you can either run 
```bash
/usr/bin/security find-generic-password -w -s "{FILE_NAME}" login.keychain-db
```
in your terminal, or open up the `Keychain Access` application and search for the filename. This will give back your password with a comma and then a number made up of the 4 numbers inputted by the dials.
