from pwn import *
from Crypto.Random.random import getrandbits
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

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
key = s.to_bytes(256, "little")[:16]

io.recvn(len('B? '))
io.sendline(hex(B).encode())

ciphertext = io.recvregex(br'Flag Ciphertext .*: (.+)\n', capture=True).group(1).decode()
ciphertext = bytes.fromhex(ciphertext)

cipher = AES.new(key=key, mode=AES.MODE_CBC, iv=ciphertext[:AES.block_size])
flag = cipher.decrypt(ciphertext[AES.block_size:])
flag = unpad(flag, cipher.block_size)

print(flag.decode())
