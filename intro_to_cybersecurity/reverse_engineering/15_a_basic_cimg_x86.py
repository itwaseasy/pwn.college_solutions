import sys

class CImgFile:
    def __init__(self):
        self.version = 2
        self.width = 46
        self.height = 23
        self.data = bytearray(self.width * self.height * 4)

        self.generate()

    def __header(self):
        return b'cIMG' + \
                int.to_bytes(self.version, 8, 'little') + \
                int.to_bytes(self.width, 2, 'little') + \
                int.to_bytes(self.height, 2, 'little')

    def generate(self):
        for h in range(self.height):
            for w in range(self.width):
                index = (h * self.width + w) * 4
                self.data[index] = 0x8c
                self.data[index+1] = 0x1d
                self.data[index+2] = 0x40
                self.data[index+3] = ord('A')

    def save(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.__header())
            f.write(self.data)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    CImgFile().save(sys.argv[1])
