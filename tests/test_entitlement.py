import datetime
from unittest import TestCase

from core_utils.entitlement import Entitlement
from core_utils.encryptor import Encryptor


class EntitlementTest(TestCase):
    def test_entitlement(self):
        private_key, public_key = Encryptor.generate_key_pair()

        ent_content = {'text': 'some license'}

        p = Entitlement(private_key)
        p.created_at = datetime.datetime.now()
        p.expired_at = datetime.datetime.now() + datetime.timedelta(days=1)
        p.content = ent_content
        permit = p.export_data('Authmachine')

        p = Entitlement(public_key)
        p.import_data(permit)

        self.assertIn('Authmachine', permit)
        self.assertEqual(p.content, ent_content)

    def test_encryptor(self):
        private_key, public_key = Encryptor.generate_key_pair()
        e = Encryptor()

        e.load_key(private_key)
        encrypted = e.encrypt("test message")

        e.load_key(public_key)
        decrypted = e.decrypt(encrypted)

        self.assertEqual(decrypted, 'test message')
