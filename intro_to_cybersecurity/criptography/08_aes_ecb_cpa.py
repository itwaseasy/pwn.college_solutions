import string

from pwn import *

io = process(['/challenge/run'])

def get_encrypted_flag_data(index, length):
    io.recvregex(br'.+\nChoice\? ')
    io.sendline(b'2')

    io.recvregex(br'Index\? ')
    io.sendline(str(index).encode())

    io.recvregex(br'Length\? ')
    io.sendline(str(length).encode())

    return io.recvregex(br'Result: (.+)\n', capture=True).group(1)

def encrypt_data(data):
    io.recvregex(br'.+\nChoice\? ')
    io.sendline(b'1')

    io.recvregex(br'Data\? ')
    io.sendline(data.encode())

    return io.recvregex(br'Result: (.+)\n', capture=True).group(1)
    
def generate_decrypt_table():
    decrypt_table = {}

    # Encrypt each character in the set separately and build a lookup table.
    for flag_char in (string.ascii_letters + string.digits + string.punctuation):
        result = encrypt_data(flag_char)
        decrypt_table[result] = flag_char

    return decrypt_table


decrypt_table = generate_decrypt_table()
encrypted_flag = bytes.fromhex(get_encrypted_flag_data(0, -1).decode())
flag = ''

for n in range(len(encrypted_flag)):
    # Encrypt one character at a time and look up the result in the table we built earlier.
    enc_flag_char = get_encrypted_flag_data(n, 1) 
    flag_char = decrypt_table[enc_flag_char]

    flag += flag_char
    print(flag)

    if bytes.fromhex(encrypt_data(flag).decode()) == encrypted_flag:
        break


