import sys

class CImgFile:
    def __init__(self):
        self.version = 2
        self.width = 4
        self.height = 1
        self.data = bytearray(self.width * self.height * 4)

        self.generate()

    def __header(self):
        return b'cIMG' + \
                int.to_bytes(self.version, 2, 'little') + \
                int.to_bytes(self.width, 1, 'little') + \
                int.to_bytes(self.height, 1, 'little')

    def generate(self):
        self.data = bytes([
                0xba, 0xb3, 0x82, ord('c'),
                0x1a, 0x56, 0x41, ord('I'),
                0xd6, 0xde, 0x7d, ord('M'),
                0x8a, 0x62, 0xf6, ord('G')])

    def save(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.__header())
            f.write(self.data)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    CImgFile().save(sys.argv[1])
