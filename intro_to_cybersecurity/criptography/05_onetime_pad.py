from pwn import *
from Crypto.Util.strxor import strxor

io = process(['/challenge/run'])

key = io.recvregex(br'One-Time .+: (.+)\n', capture=True).group(1).decode()
secret = io.recvregex(br'Flag .+: (.+)\n', capture=True).group(1).decode()

answer = strxor(bytes.fromhex(key), bytes.fromhex(secret))

print(answer.decode())
