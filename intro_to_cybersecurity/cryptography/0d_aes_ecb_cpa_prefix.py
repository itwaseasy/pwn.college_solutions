from pwn import *
from Crypto.Cipher import AES

io = process(['/challenge/run'])

def get_encrypted_flag_data(data):
    io.recvregex(br'.+\nChoice\? ')
    io.sendline(b'2')

    io.recvregex(br'Data\? ')
    io.sendline(data)

    return bytes.fromhex(io.recvregex(br'Result: (.+)\n', capture=True).group(1).decode())

def encrypt_data(data):
    io.recvregex(br'.+\nChoice\? ')
    io.sendline(b'1')

    io.recvregex(br'Data\? ')
    io.sendline(data)

    return bytes.fromhex(io.recvregex(br'Result: (.+)\n', capture=True).group(1).decode())
    
def generate_decrypt_table(prefix):
    decrypt_table = {}

    for flag_char in (string.ascii_letters + string.digits + string.punctuation):
        data = (prefix + flag_char).encode()
        result = encrypt_data(data)
        decrypt_table[result] = flag_char

    return decrypt_table


# Calculate the number of blocks in which the flag is encoded.
ciphertext = get_encrypted_flag_data(b'')
number_of_blocks = len(ciphertext) // AES.block_size

# The "working block" is the last block that is used for iteration.
working_block_start = (number_of_blocks - 1) * AES.block_size
working_block_end = working_block_start + AES.block_size

flag = ''
padding = bytearray()

# Calculate the exact string that needs to be added to the beginning
# to encode the flag without padding.
while True:
    padding += b'A'
    padded_ciphertext = get_encrypted_flag_data(padding)
    if len(padded_ciphertext) // AES.block_size > number_of_blocks:
        padding = padding[:-1]
        break

# The original number of blocks remains the same, and we know the exact
# padding length, so we can now calculate the flag length.
flag_length = number_of_blocks * AES.block_size - len(padding)

# Adjust the fill string so that the last character of the working block
# (the one used for brute-force) contains the first character of the flag.
padding = padding + b'A'*(flag_length - 1)

# So now block_cleartext = 'AAAAAAAAAAAAAAA?' where '?' will be the first
# character of the flag.
block_cleartext = padding[-(AES.block_size - 1):].decode()

for _ in range(flag_length):
    # Encrypt the flag with the required padding and get the working block
    # from the ciphertext.
    current_ciphertext = get_encrypted_flag_data(padding)
    data_to_check = current_ciphertext[working_block_start : working_block_end]

    decrypt_table = generate_decrypt_table(block_cleartext)

    flag_char = decrypt_table[data_to_check]
    flag += flag_char

    # Add the next character found to block_cleartext and remove the first one,
    # a sort of homemade circular buffer.
    block_cleartext += flag_char
    block_cleartext = block_cleartext[1:]
    padding = padding[:-1]

    print(flag)
