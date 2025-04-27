from pwn import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

io = process(['/challenge/run'])

key = io.recvregex(br'AES Key .+: (.+)\n', capture=True).group(1).decode()
secret = io.recvregex(br'Flag .+: (.+)\n', capture=True).group(1).decode()

key = bytes.fromhex(key)
secret = bytes.fromhex(secret)

cipher = AES.new(key=key, mode=AES.MODE_ECB)
answer = cipher.decrypt(secret)
answer = unpad(answer, AES.block_size)

print(answer.decode())
