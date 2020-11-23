class EncryptorError(Exception):
    pass


class EncryptionError(EncryptorError):
    pass


class EncryptorKeyError(EncryptorError):
    pass


class DecryptionError(EncryptorError):
    pass


class EntitlementError(Exception):
    pass


class ValidationError(Exception):
    pass
