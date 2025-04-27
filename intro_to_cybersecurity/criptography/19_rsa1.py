from pwn import *

io = process(['/challenge/run'])

n_hex = io.recvregex(br'.+ n = (.+)\n', capture=True).group(1).decode()
e_hex = io.recvregex(br'.+ e = (.+)\n', capture=True).group(1).decode()
d_hex = io.recvregex(br'.+ d = (.+)\n', capture=True).group(1).decode()

n = int(n_hex, 16)
d = int(d_hex, 16)

flag_ciphertext = io.recvregex(br'Flag Ciphertext .*: (.+)\n', capture=True).group(1).decode()
flag_ciphertext = bytes.fromhex(flag_ciphertext)

flag = pow(int.from_bytes(flag_ciphertext, "little"), d, n).to_bytes(256, "little")
print(flag.decode().rstrip('\0'))

