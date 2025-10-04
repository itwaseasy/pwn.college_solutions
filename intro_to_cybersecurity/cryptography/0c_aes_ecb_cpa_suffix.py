from pwn import *

io = process(['/challenge/run'])

def get_encrypted_flag_data(length):
    io.recvregex(br'.+\nChoice\? ')
    io.sendline(b'2')

    io.recvregex(br'Length\? ')
    io.sendline(str(length).encode())

    return io.recvregex(br'Result: (.+)\n', capture=True).group(1)

def encrypt_data(data):
    io.recvregex(br'.+\nChoice\? ')
    io.sendline(b'1')

    io.recvregex(br'Data\? ')
    io.sendline(data.encode())

    return io.recvregex(br'Result: (.+)\n', capture=True).group(1)
    
def generate_decrypt_table(suffix):
    decrypt_table = {}

    # Add each character from the set to the suffix, encrypt it, and build a lookup table.
    for flag_char in (string.ascii_letters + string.digits + string.punctuation):
        result = encrypt_data(flag_char + suffix)
        decrypt_table[result] = flag_char

    return decrypt_table


encrypted_flag = bytes.fromhex(get_encrypted_flag_data(0).decode())
flag = ''

for n in range(1, len(encrypted_flag)):
    # Rebuild the lookup table based on the suffix we already know.
    decrypt_table = generate_decrypt_table(flag)

    # Get n characters of the encrypted flag (the one we need to find + the suffix we know)
    # and find the result in the table.
    enc_flag_char = get_encrypted_flag_data(n) 
    flag_char = decrypt_table[enc_flag_char]

    flag = flag_char + flag
    print(flag)

    if bytes.fromhex(encrypt_data(flag).decode()) == encrypted_flag:
        break

