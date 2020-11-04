from spa.secrets import password_encrypt, password_decrypt

message = 'Huu Nguyen'
password = 'some key for secret'
en = password_encrypt(message.encode(), password)
de = password_decrypt(en, password).decode()

print(de)