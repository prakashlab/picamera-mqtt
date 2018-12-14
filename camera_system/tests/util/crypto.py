"""Test the util.crypto module."""
from intervention_system.util import crypto

def main():
    box = crypto.generate_box()
    string_plain = 'hello, world!'
    string_cipher = crypto.string_encrypt(string_plain, box)
    assert isinstance(string_cipher, str)
    assert string_plain == crypto.string_decrypt(string_cipher, box)
    obj_plain = {'foo': 'bar'}
    string_cipher = crypto.json_secret_dumps(obj_plain, box)
    assert isinstance(string_cipher, str)
    assert crypto.json_secret_loads(string_cipher, box)['foo'] == 'bar'
    string_cipher_2 = crypto.json_secret_dumps(obj_plain, box)
    assert string_cipher != string_cipher_2

if __name__ == '__main__':
    main()
