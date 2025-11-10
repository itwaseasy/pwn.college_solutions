import sys
import os
import re

class CImgFile:
    def __init__(self):
        self.version = 3
        self.width = 53
        self.height = 17
        self.directives = {'load_data' : 0xd849}
        self.data = bytearray()


    def __header(self):
        return b'cIMG' + \
                int.to_bytes(self.version, 2, 'little') + \
                int.to_bytes(self.width, 1, 'little') + \
                int.to_bytes(self.height, 1, 'little') + \
                int.to_bytes(len(self.directives), 4, 'little')

    def __data(self):
        return int.to_bytes(self.directives['load_data'], 2, 'little') + \
                self.data

    def load_ansi(self, filename):
        r = re.compile(br'.\[\d+;\d+;(\d+);(\d+);(\d+)m(.).+')
        with open(filename, 'rb') as f:
            while chr_line := f.read(24):
                m = r.search(chr_line)
                self.data += \
                        int(m.group(1)).to_bytes(1) + \
                        int(m.group(2)).to_bytes(1) + \
                        int(m.group(3)).to_bytes(1) + \
                        m.group(4)


    def save(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.__header())
            f.write(self.__data())

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    f = CImgFile()
    f.load_ansi(f'{os.path.splitext(sys.argv[0])[0] + ".ansi"}')
    f.save(sys.argv[1])
