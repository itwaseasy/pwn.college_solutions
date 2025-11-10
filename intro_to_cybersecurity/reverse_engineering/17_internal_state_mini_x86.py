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
                0xc8, 0x28, 0x83, ord('c'),
                0x01, 0x13, 0xa5, ord('I'),
                0xa0, 0x86, 0x3b, ord('M'),
                0xc3, 0x2e, 0x4f, ord('G')])

    def save(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.__header())
            f.write(self.data)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    CImgFile().save(sys.argv[1])
