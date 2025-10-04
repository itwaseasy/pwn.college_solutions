from pwn import *
from Crypto.Util.strxor import strxor

io = process(['/challenge/dispatcher'])

dispatcher_secret = io.recvregex(br'TASK: (.+)\n', capture=True).group(1).decode()
dispatcher_secret = bytes.fromhex(dispatcher_secret)

x = strxor(dispatcher_secret, b"sleep")
x = strxor(x, b"flag!")

io.kill()
io = process(['/challenge/worker'])

io.sendline(("TASK: " + x.hex()).encode())

flag = io.recvregex(br'Your flag:\n(.+)\n', capture=True).group(1)
print(flag.decode())
