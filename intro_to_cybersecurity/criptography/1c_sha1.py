import itertools

from pwn import *

def find_colliding(flag_hash):
    for k in range (10):
        for bf_data in itertools.combinations([i for i in range(1,255)], k):
            bf_data_hash = hashlib.sha256(bytes(bf_data)).hexdigest()
            if flag_hash == bf_data_hash[:len(flag_hash)]:
                return bytes(bf_data)

    return None

io = process(['/challenge/run'])

flag_hash = io.recvregex(br'flag_hash.*=\'(.+)\'\n', capture=True).group(1).decode()

colliding_data = find_colliding(flag_hash)

io.readn(len('Colliding input? '))
io.sendline(colliding_data.hex().encode())

flag = io.recvregex(br'Collided.+\n(.+)\n', capture=True).group(1).decode()
print(flag)

