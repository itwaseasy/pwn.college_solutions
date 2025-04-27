import string
import requests
import re

result_rx = re.compile(r'.*Results:.+<pre>(.+)</pre>\n.*')

def encrypt_data_query(query):
    r = requests.get(url = 'http://challenge.localhost/', params = {'query': f'{query}'})
    ciphertext = result_rx.search(r.text).group(1)

    return bytes.fromhex(ciphertext)
    
def generate_decrypt_table():
    decrypt_table = {}

    # Encrypt each character in the set separately and build a lookup table.
    for flag_char in (string.ascii_letters + string.digits + string.punctuation + '\n'):
        delimiter = "'" if flag_char == '"' else '"'
        result = encrypt_data_query(delimiter + flag_char + delimiter)
        decrypt_table[result] = flag_char

    return decrypt_table


decrypt_table = generate_decrypt_table()
encrypted_flag = encrypt_data_query("flag")
flag = ''

for n in range(len(encrypted_flag)):
    # Encrypt one character at a time and look up the result in the table we built earlier.
    enc_flag_char = encrypt_data_query(f'substr(flag, {n + 1}, 1)')
    flag_char = decrypt_table[enc_flag_char]

    flag += flag_char
    print(flag)

    if encrypt_data_query(f'"{flag}"') == encrypted_flag:
        break
