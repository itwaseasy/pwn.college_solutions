import itertools

from pwn import *
from base64 import b64decode, b64encode

def find_hash(challenge, difficulty):
    for k in range (10):
        for bf_data in itertools.combinations([i for i in range(1,255)], k):
            bf_data_hash = hashlib.sha256(challenge + bytes(bf_data)).digest()
            if bf_data_hash[:difficulty] == (b'\0' * difficulty):
                return bytes(bf_data)

    return None


io = process(['/challenge/run'])

challenge = io.recvregex(br'challenge.*: (.+)\n', capture=True).group(1).decode()
challenge = b64decode(challenge)

response = find_hash(challenge, 2)

io.readn(len('response (b64): '))
io.sendline(b64encode(response))

flag = io.recvregex(br'flag: (.+)\n', capture=True).group(1).decode()
print(flag)

