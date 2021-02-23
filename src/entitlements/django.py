from django.db import models
from django.utils.functional import cached_property

from .entitlement import Entitlement


class Model(models.Model):
    license_data = models.TextField()

    class Meta:
        abstract = True

    def load_data(self):
        if '__ent' in self.__dict__:
            del self.__dict__['__ent']

        ent = Entitlement(self.pubkey)
        ent.import_data(self.license_data)
        self.__dict__['__ent'] = ent

    def __getattribute__(self, item):
        if not item.startswith('__') and item in self.__dict__:
            return self.__dict__[item]
        return super().__getattribute__(item)

    @property
    def properties(self):
        if '__ent' not in self.__dict__:
            Model.load_data(self)
        return self.__dict__['__ent'].content

    @property
    def expired_at(self):
        if '__ent' not in self.__dict__:
            Model.load_data(self)

        ent = self.__dict__['__ent']
        ent_data = ent.to_dict()
        return ent_data["expired_at"] if "expired_at" in ent_data else None

    @property
    def is_valid(self):
        if '__ent' not in self.__dict__:
            Model.load_data(self)
        ent = self.__dict__['__ent']
        return ent.is_valid and not ent.is_expired

    @cached_property
    def pubkey(self):
        return self.get_pubkey()

    def get_property(self, key, default=None):
        return self.properties.get(key, default)

    def get_pubkey(self):
        raise NotImplementedError

    @classmethod
    def get_current(cls):
        raise NotImplementedError
