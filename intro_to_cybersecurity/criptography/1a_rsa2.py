from pwn import *

io = process(['/challenge/run'])

e_hex = io.recvregex(br'e = (.+)\n', capture=True).group(1).decode()
p_hex = io.recvregex(br'p = (.+)\n', capture=True).group(1).decode()
q_hex = io.recvregex(br'q = (.+)\n', capture=True).group(1).decode()

e = int(e_hex, 16)
p = int(p_hex, 16)
q = int(q_hex, 16)

n = p*q
phi = (p-1)*(q-1)
d = pow(e, -1, phi)

flag_ciphertext = io.recvregex(br'Flag Ciphertext .*: (.+)\n', capture=True).group(1).decode()
flag_ciphertext = bytes.fromhex(flag_ciphertext)

flag = pow(int.from_bytes(flag_ciphertext, "little"), d, n).to_bytes(256, "little")
print(flag.decode().rstrip('\0'))

