from cryptography.fernet import Fernet


def encrypt(message: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(message)


def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)


key = Fernet.generate_key()  # store in a secure location
print("Key:", key.decode())
message = 'Huu Nguyen'
en = encrypt(message.encode(), key)
print(en)
de = decrypt(en, key).decode()
print(de)
