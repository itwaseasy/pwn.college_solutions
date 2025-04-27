from pwn import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Util.strxor import strxor

def decrypt_block(io, block):
    work_block = bytearray(AES.block_size)
    original_block = bytearray(AES.block_size)

    byte_index = AES.block_size - 1
    pad_counter = 1

    while byte_index >= 0:
        io.sendline(("TASK: " + work_block.hex() + block.hex()).encode())

        response = io.recvline()
        if not response.startswith(b"Unknown"):
            work_block[byte_index] += 1
            continue

        original_block[byte_index] = work_block[byte_index] ^ pad_counter

        pad_counter += 1
        byte_index -= 1

        for n in range (AES.block_size - 1, byte_index, -1):
            work_block[n] = original_block[n] ^ pad_counter

    return original_block


io = process(['/challenge/dispatcher', "flag"])

pw = io.recvregex(br'TASK: (.+)\n', capture=True).group(1).decode()
pw = bytes.fromhex(pw)
pw_blocks = len(pw) // AES.block_size

io.kill()
io = process(['/challenge/worker'])

cleartext = bytearray()

for n in range (pw_blocks - 1, 0, -1):
    encrypted_block_start = n * AES.block_size
    encrypted_block_end = encrypted_block_start + AES.block_size

    encrypted_block = pw[encrypted_block_start : encrypted_block_end]
    previous_block = pw[encrypted_block_start - AES.block_size : encrypted_block_start]

    original_block = decrypt_block(io, encrypted_block)

    cleartext = strxor(original_block, previous_block) + cleartext

print(unpad(cleartext, AES.block_size).decode())
