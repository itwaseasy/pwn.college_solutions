import string
import requests
import re

from Crypto.Cipher import AES
from base64 import b64decode

challenge_url = 'http://challenge.localhost'
result_rx = re.compile(r'.*Encrypted backup:.+<pre>(.+)</pre>\n.*')

def encrypt_data(data):
    if data is not None:
        requests.post(url = challenge_url, data = {'content' : data.decode()})

    r = requests.get(url = challenge_url)
    ciphertext = result_rx.search(r.text).group(1)

    if data is not None:
        requests.post(url = challenge_url + '/reset')

    return b64decode(ciphertext)
    
def generate_decrypt_table(prefix):
    decrypt_table = {}

    for flag_char in (string.ascii_letters + string.digits + string.punctuation):
        data = (prefix + flag_char).encode()
        
        # We are asking to encrypt data that is exactly 16 bytes long, and the remaining flag 
        # will be appended to it to form the plaintext. As a result, the data we need will be
        # in the first block of the ciphertext
        result = encrypt_data(data)[:AES.block_size]

        decrypt_table[result] = flag_char

    return decrypt_table

# Calculate the number of blocks in which the flag is encoded.
ciphertext = encrypt_data(None)
number_of_blocks = len(ciphertext) // AES.block_size

# The "working block" is the last block that is used for iteration.
working_block_start = (number_of_blocks - 1) * AES.block_size
working_block_end = working_block_start + AES.block_size

flag = ''
padding = bytearray()

# Calculate the exact string that needs to be added to the beginning
# to encode the flag without padding. Note that the server appends
# the '|' character by default.
while True:
    padded_ciphertext = encrypt_data(padding)
    if len(padded_ciphertext) // AES.block_size > number_of_blocks:
        padding = padding[:-1]
        break

    padding += b'A'

# The original number of blocks remains the same, and we know the exact
# padding length, so we can now calculate the flag length.
flag_length = number_of_blocks * AES.block_size - len(padding)

# Adjust the fill string so that the last character of the working block
# (the one used for brute-force) contains the first character of the flag.
# The server adds the | character by default, so we need to take that into
# account.
padding = padding + b'A'*(flag_length - 2)

# So now block_cleartext = 'AAAAAAAAAAAAAAA?' where '?' will be the first
# character of the flag.
# Again, the | character should be taken into account.
block_cleartext = padding[-(AES.block_size - 2):]
block_cleartext = (block_cleartext + b'|').decode()

for _ in range(flag_length - 2):
    # Encrypt the flag with the required padding and get the working block
    # from the ciphertext.
    current_ciphertext = encrypt_data(padding)
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
