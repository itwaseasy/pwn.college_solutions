from pwn import *
from Crypto.Random.random import getrandbits

io = process(['/challenge/run'])

p_hex = io.recvregex(br'p = (.+)\n', capture=True).group(1).decode()
g_hex = io.recvregex(br'g = (.+)\n', capture=True).group(1).decode()
A_hex = io.recvregex(br'A = (.+)\n', capture=True).group(1).decode()

p = int(p_hex, 16)
g = int(g_hex, 16)
A = int(A_hex, 16)

b = getrandbits(2048)
B = pow(g, b, p)

s = pow(A, b, p)

io.recvn(len('B? '))
io.sendline(hex(B).encode())

io.recvn(len('s? '))
io.sendline(hex(s).encode())

flag = io.recvregex(br'your flag:\n(.+)\n', capture=True).group(1).decode()
print(flag)
