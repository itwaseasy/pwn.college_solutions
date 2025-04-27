from pwn import *
from Crypto.Util.strxor import strxor

io = process(['/challenge/run'], stdin=PTY)

for _ in range(1, 10):
    enc_string = io.recvregex(br'- Encrypted String: (.+)\n', capture=True).group(1)
    key  = io.recvregex(br'- XOR Key String: (.+)\n', capture=True).group(1)

    answer = strxor(enc_string, key)

    io.recvn(len("- Decrypted String? "))
    io.sendline(answer)

    io.recvline_endswith(b'Moving on.')

flag = io.recvregex(br'.+flag:\n(.+)\n', capture=True).group(1).decode()
print(flag)
