import datetime
import json

from .encryptor import Encryptor, EncryptorError
from .boundary import remove_boundary, add_boundary
from .exceptions import EntitlementError


__all__ = ['Entitlement', 'EntitlementError']


class Entitlement:
    content = None
    _created_at = None
    _expired_at = None

    def __init__(self, encryption_key):
        self._encryption_key = encryption_key

    @classmethod
    def to_ts(cls, datetime_=None):
        if datetime_ is None:
            datetime_ = datetime.datetime.now()
        return datetime_.timestamp()

    @property
    def expired_at(self):
        if self._expired_at is None:
            return None
        return datetime.datetime.fromtimestamp(self._expired_at)

    @expired_at.setter
    def expired_at(self, value):
        if isinstance(value, datetime.datetime):
            value = self.to_ts(value)
        self._expired_at = value

    @property
    def created_at(self):
        if self._created_at is None:
            return None
        return datetime.datetime.fromtimestamp(self._created_at)

    @created_at.setter
    def created_at(self, value):
        if isinstance(value, datetime.datetime):
            value = self.to_ts(value)
        self._created_at = value

    @property
    def is_expired(self):
        expired_date_plus_three_weeks = datetime.datetime.fromtimestamp(self._expired_at) + datetime.timedelta(days=0)
        return self._expired_at is not None and self.to_ts() > expired_date_plus_three_weeks.timestamp()

    @property
    def is_valid(self):
        is_valid = True
        is_valid = is_valid and isinstance(self.content, dict)
        is_valid = is_valid and isinstance(self.created_at, datetime.datetime)
        is_valid = is_valid and (isinstance(self.expired_at, datetime.datetime) or
                                 self.expired_at is None)
        return is_valid

    def to_dict(self):
        return {
            'content': self.content,
            'created_at': self._created_at,
            'expired_at': self._expired_at,
        }

    def import_data(self, data):
        data = remove_boundary(data)

        encryptor = Encryptor()
        try:
            encryptor.load_key(self._encryption_key)
            json_data = encryptor.decrypt(data)
        except EncryptorError as err:
            raise EntitlementError(
                "Permit data could not be decrypted."
            ) from err

        try:
            attrs = json.loads(json_data)
        except json.JSONDecodeError as err:
            raise EntitlementError(
                "Permit data is invalid JSON."
            ) from err

        for key, value in attrs.items():
            setattr(self, key, value)

    def export_data(self, boundary=None):
        self.validate()

        encryptor = Encryptor()
        try:
            encryptor.load_key(self._encryption_key)
            encrypted = encryptor.encrypt(json.dumps(self.to_dict()))
            encrypted = encrypted.decode()
        except EncryptorError as err:
            raise EntitlementError(
                "Permit data could not be encrypted."
            ) from err

        if boundary is not None:
            encrypted = add_boundary(encrypted, boundary)

        return encrypted

    def validate(self):
        if not self.is_valid:
            raise EntitlementError("The entitlement is invalid")
