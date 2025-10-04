from pwn import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.strxor import strxor

io = process(['/challenge/dispatcher'])

dispatcher_secret = io.recvregex(br'TASK: (.+)\n', capture=True).group(1).decode()
dispatcher_secret = bytes.fromhex(dispatcher_secret)

x = strxor(dispatcher_secret[:AES.block_size], pad(b"sleep", AES.block_size))
x = strxor(x, pad(b"flag!", AES.block_size))

io.kill()
io = process(['/challenge/worker'])

io.sendline(("TASK: " + x.hex() + dispatcher_secret[AES.block_size:].hex()).encode())

flag = io.recvregex(br'Your flag:\n(.+)\n', capture=True).group(1)
print(flag.decode())
