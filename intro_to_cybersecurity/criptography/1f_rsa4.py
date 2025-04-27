from pwn import *
from Crypto.PublicKey import RSA
from base64 import b64decode

io = process(['/challenge/run'])

key = RSA.generate(1024)

io.recvn(len('e: '))
io.sendline(hex(key.e).encode())

io.recvn(len('n: '))
io.sendline(hex(key.n).encode())

challenge_hex = io.recvregex(br'challenge: (.+)\n', capture=True).group(1).decode()
challenge = int(challenge_hex, 16)

response = pow(challenge, key.d, key.n)

io.recvn(len('response: '))
io.sendline(hex(response).encode())

ciphertext = io.recvregex(br'.+ ciphertext.*: (.+)\n', capture=True).group(1).decode()
ciphertext = b64decode(ciphertext)

flag = pow(int.from_bytes(ciphertext, "little"), key.d, key.n).to_bytes(256, "little")
print(flag.decode().rstrip('\0'))
