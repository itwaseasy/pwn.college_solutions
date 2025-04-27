from pwn import *

io = process(['/challenge/run'], stdin=PTY)

for _ in range(1, 10):
    enc_char = io.recvregex(br'- Encrypted Character: (.+)\n', capture=True).group(1)
    key  = io.recvregex(br'- XOR Key: (.+)\n', capture=True).group(1)

    answer = chr(ord(enc_char) ^ int(key, 16))

    io.recvn(len("- Decrypted Character? "))
    io.sendline(answer.encode())

    io.recvline_endswith(b'Moving on.')

flag = io.recvregex(br'.+flag:\n(.+)\n', capture=True).group(1).decode()
print(flag)
