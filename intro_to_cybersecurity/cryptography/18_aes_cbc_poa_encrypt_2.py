from pwn import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
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


io = process(['/challenge/worker'])

cleartext = pad(b'please give me the flag, kind worker process!', AES.block_size)
ct_blocks = len(cleartext) // AES.block_size

guess_block = bytearray(os.urandom(16))
ciphertext = bytearray(guess_block)

for n in range (ct_blocks - 1, -1, -1):
    ct_block_start = n * AES.block_size
    ct_block_end = ct_block_start + AES.block_size

    ct_block = cleartext[ct_block_start : ct_block_end]

    decrypted_guess = decrypt_block(io, guess_block)
    previous_block = strxor(ct_block, decrypted_guess)

    ciphertext = previous_block + ciphertext
    guess_block = previous_block

io.sendline(("TASK: " + ciphertext.hex()).encode())

flag = io.recvregex(br'Your flag:\n(.+)\n', capture=True).group(1).decode()
print(flag)
