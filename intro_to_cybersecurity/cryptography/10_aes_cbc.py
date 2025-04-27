from pwn import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

io = process(['/challenge/run'])

key = io.recvregex(br'AES Key .+: (.+)\n', capture=True).group(1).decode()
secret = io.recvregex(br'Flag .+: (.+)\n', capture=True).group(1).decode()

key = bytes.fromhex(key)
secret = bytes.fromhex(secret)

cipher = AES.new(key=key, mode=AES.MODE_CBC, iv=secret[:AES.block_size])
answer = cipher.decrypt(secret[cipher.block_size:])
answer = unpad(answer, cipher.block_size)

print(answer.decode())
