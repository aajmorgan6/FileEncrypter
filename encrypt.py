import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

import os
import base64
import pathlib
import keyring

def read_secret_string(filename: str) -> str:
    """Returns the secret string."""
    pw = keyring.get_password(filename, "FileEncrypter")
    return pw if pw else ""  # make sure to return str for type hint


def write_secret_string(filename: str, secret_string: str) -> bool:
    """Writes the secret string."""
    try:
        keyring.set_password(filename, "FileEncrypter", secret_string)
        return True 
    except keyring.errors.PasswordSetError as e:
        print(f"    The attempted write to the login keychain failed.")
        return False
    

def delete_keychain(filename: str) -> bool:
    try:
        keyring.delete_password(filename, "FileEncrypter")
        return True
    
    except keyring.errors.PasswordDeleteError as e:
        print("      The attempted delete to the login keychain failed.")
        return False
    

def make_key(salt: bytes, password: str) -> bytes:
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    derived = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(derived)

def encrypt_file_algo(encrypt_file: str, key: bytes) -> None:
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