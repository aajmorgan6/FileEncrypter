import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

import os
import base64
import pathlib

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