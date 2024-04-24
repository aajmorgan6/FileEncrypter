import cryptography #type: ignore
from cryptography.fernet import Fernet #type: ignore
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt #type: ignore

import os
import base64
import pathlib
import platform
from subprocess import CalledProcessError, run
import keyring #type: ignore

def read_secret_string(filename):
    """Returns the secret string."""
    if platform.system() == "Darwin":
        return from_keychain(filename)
    # elif platform.system() == "Windows":
    #     return from_locker()


def write_secret_string(filename, secret_string):
    """Writes the secret string."""
    if platform.system() == "Darwin":
        to_keychain(filename, secret_string)
    # elif platform.system() == "Windows":
    #     to_locker(secret_string) 

def from_keychain(filename):
    """ """
    arg_list = [
        "/usr/bin/security",
        "find-generic-password",
        "-w",
        "-s",
        filename,
        "-a",
        "test",
        "login.keychain-db",
    ]
    try:
        cp = run(arg_list, check=True, text=True, capture_output=True)
        key_str = cp.stdout.rstrip()
        return key_str
    except CalledProcessError as e:
        print(f"    The attempted read from the login keychain failed.")
        return None

def to_keychain(filename, secret_key_string):
    """Save secret key string to keychain"""
    arg_list = [
        "/usr/bin/security",
        "add-generic-password",
        "-s",
        filename,
        "-a",
        "test",
        "-w",
        secret_key_string,
        "login.keychain-db",
    ]
    try:
        run(arg_list, check=True, text=True, capture_output=True)
        return True
    except CalledProcessError as e:
        print(f"    The attempted write to the login keychain failed.")

def make_key(salt: bytes, password: str):
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    derived = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(derived)

def encrypt_file_algo(encrypt_file, key) -> None:
    '''
    Key will come from both password and seed
    '''
    f = Fernet(key)
    with open(encrypt_file, "rb") as infile:
        to_encrypt = infile.read()

    encrypted = f.encrypt(to_encrypt)
    with open(encrypt_file+".box", "wb") as outfile:
        outfile.write(encrypted)
    # TODO: delete old file?, or just overwrite 
    os.remove(pathlib.Path(encrypt_file))
        

def decrypt_file_algo(decrypt_file: str, key) -> bool:

    f = Fernet(key)
    with open(decrypt_file, "rb") as infile:
        to_decrypt = infile.read()

    try:
        decrypted = f.decrypt(to_decrypt)
    except cryptography.fernet.InvalidToken:
        print("Invalid token")
        return False 
    
    with open(decrypt_file[:-len('.box')], "wb") as outfile:
        outfile.write(decrypted)

    os.remove(pathlib.Path(decrypt_file))
    return True