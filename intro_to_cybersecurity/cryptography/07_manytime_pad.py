from pwn import *

io = process(['/challenge/run'])

ciphertext = io.recvregex(br'Flag .+: (.+)\n', capture=True).group(1).decode()
ciphertext = bytes.fromhex(ciphertext)

flag = bytearray(len(ciphertext))
flag[-1] = ord('\n')

for n in range(len(ciphertext) - 1):
    for flag_char in (string.ascii_letters + string.digits + string.punctuation).encode():
        flag[n] = flag_char

        io.recvn(len('Plaintext (hex): '))
        io.sendline(flag.hex().encode())

        enc_flag = io.recvregex(br'Ciphertext .+: (.+)\n', capture=True).group(1).decode()
        enc_flag = bytes.fromhex(enc_flag)

        if enc_flag[n] == ciphertext[n]:
            print(flag[:n].decode())
            break

print(flag.decode())
