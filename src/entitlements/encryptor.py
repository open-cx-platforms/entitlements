import json
from base64 import b64encode, b64decode

from Cryptodome import Random
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256
from Cryptodome.Signature import pkcs1_15

from .exceptions import EncryptorError, EncryptionError, EncryptorKeyError, DecryptionError

__all__ = ["EncryptorError", "EncryptorKeyError", "EncryptionError",
           "DecryptionError", "Encryptor"]


class Encryptor:
    _rsa_key = None
    _aes_len = 32

    def load_key(self, key, passphrase=None):
        try:
            self._rsa_key = RSA.import_key(key, passphrase)
        except (ValueError, IndexError, TypeError):
            raise EncryptorKeyError("No RSA encryption key provided.")

    @classmethod
    def generate_key_pair(cls, key_length=1024):
        key = RSA.generate(key_length)
        pub_key = key.publickey()
        return key.exportKey(), pub_key.exportKey()

    @classmethod
    def get_public_key(cls, private_key, passphrase=None):
        key = RSA.import_key(private_key, passphrase)
        return key.publickey().export_key()

    def encrypt(self, data):
        if self._rsa_key is None:
            raise EncryptorKeyError("No RSA encryption private key provided.")
        if not self._rsa_key.has_private():
            raise EncryptorKeyError("Provided key is not an RSA private key.")

        aes_key = Random.get_random_bytes(self._aes_len)
        cipher_aes = AES.new(aes_key, AES.MODE_OFB)
        encrypted_data = cipher_aes.encrypt(data.encode('utf-8'))

        sig = pkcs1_15.new(self._rsa_key).sign(SHA256.new(aes_key))
        encrypted_key = b"".join((sig, aes_key))

        encryption_data = {
            "data": b64encode(encrypted_data).decode('utf-8'),
            "key": b64encode(encrypted_key).decode('utf-8'),
            "iv": b64encode(cipher_aes.iv).decode('utf-8'),
        }

        return b64encode(json.dumps(encryption_data).encode('utf-8'))

    def decrypt(self, data):
        if self._rsa_key is None:
            raise EncryptorKeyError("No RSA encryption public key provided.")
        if self._rsa_key.has_private():
            raise EncryptorKeyError("Provided key is not an RSA public key.")

        try:
            json_data = json.loads(b64decode(data).decode('utf-8'))
        except json.JSONDecodeError:
            raise DecryptionError("Encryption data is invalid JSON.")

        if not all(map(lambda i: i in json_data, ('data', 'key', 'iv'))):
            raise DecryptionError(
                "Required field missing from encryption data."
            )

        encrypted_data = b64decode(json_data["data"])
        encrypted_key = b64decode(json_data["key"])
        aes_iv = b64decode(json_data["iv"])
        sig, aes_key = (encrypted_key[:-self._aes_len],
                        encrypted_key[-self._aes_len:])

        try:
            pkcs1_15.new(self._rsa_key).verify(SHA256.new(aes_key), sig)
        except (ValueError, KeyError):
            raise DecryptionError("Data could not be decrypted.")

        try:
            cipher = AES.new(aes_key, AES.MODE_OFB, iv=aes_iv)
            return cipher.decrypt(encrypted_data).decode('utf-8')
        except (ValueError, KeyError):
            raise DecryptionError("Data could not be decrypted.")
