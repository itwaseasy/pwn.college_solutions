from pwn import *
from base64 import b64encode, b64decode

def sign_command(command):
    io = process(['/challenge/dispatcher', b64encode(command)])
    signature = io.recvregex(br'Signed command .*: (.+)\n', capture=True).group(1).decode()

    io.kill()

    return b64decode(signature)


flag_part1 = 2
flag_part2 = int(int.from_bytes(b'flag', "little") / flag_part1)

flag_part1_signed = sign_command(flag_part1.to_bytes(256, "little"))
flag_part2_signed = sign_command(flag_part2.to_bytes(256, "little"))

x = int.from_bytes(flag_part1_signed, "little")
y = int.from_bytes(flag_part2_signed, "little")

answer = b64encode((x*y).to_bytes(512, "little"))

io = process(['/challenge/worker', answer])

flag = io.recvregex(br'.+ signed command: .+\n(.+)\n', capture=True).group(1).decode()
print(flag)
