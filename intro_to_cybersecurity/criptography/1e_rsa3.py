from pwn import *

io = process(['/challenge/run'])

e_hex = io.recvregex(br'e: (.+)\n', capture=True).group(1).decode()
d_hex = io.recvregex(br'd: (.+)\n', capture=True).group(1).decode()
n_hex = io.recvregex(br'n: (.+)\n', capture=True).group(1).decode()
challenge_hex = io.recvregex(br'challenge: (.+)\n', capture=True).group(1).decode()

d = int(d_hex, 16)
n = int(n_hex, 16)
challenge = int(challenge_hex, 16)

response = pow(challenge, d, n)

io.recvn(len('response: '))
io.sendline(hex(response).encode())

flag = io.recvregex(br'flag: (.+)\n', capture=True).group(1).decode()
print(flag)
