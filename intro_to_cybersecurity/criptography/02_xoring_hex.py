from pwn import *

io = process(['/challenge/run'])

for _ in range(10):
    key = io.recvregex(br'The key: (.+)\n', capture=True).group(1)
    secret = io.recvregex(br'Encrypted secret: (.+)\n', capture=True).group(1)

    answer = int(key, 16) ^ int(secret, 16)

    io.sendline(hex(answer).encode())
    io.recvline_endswith(b'Moving on.')

flag = io.recvregex(br'.+flag:\n(.+)\n', capture=True).group(1).decode()
print(flag)
