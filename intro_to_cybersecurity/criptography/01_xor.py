from pwn import *

io = process(['/challenge/run'])

key = io.recvregex(br'The key: (.+)\n', capture=True).group(1)
secret = io.recvregex(br'Encrypted secret: (.+)\n', capture=True).group(1)

answer = int(key) ^ int(secret)

io.recvn(len('Decrypted secret? '))
io.sendline(str(answer).encode())

flag = io.recvregex(br'.+flag:\n(.+)\n', capture=True).group(1).decode()
print(flag)
