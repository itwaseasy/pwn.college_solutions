import sys

class CImgFile:
    def __init__(self):
        self.version = 1
        self.width = 11 
        self.height = 25
        self.data = bytearray(self.width * self.height)

        self.generate()

    def __header(self):
        return b'cIMG' + \
                int.to_bytes(self.version, 8, 'little') + \
                int.to_bytes(self.width, 1, 'little') + \
                int.to_bytes(self.height, 2, 'little')

    def generate(self):
        for h in range(self.height):
            for w in range(self.width):
                index = h * self.width + w
                self.data[index] = ord('A')

    def save(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.__header())
            f.write(self.data)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    CImgFile().save(sys.argv[1])
