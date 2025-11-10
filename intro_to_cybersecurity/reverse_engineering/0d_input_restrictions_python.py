import sys

class CImgFile:
    def __init__(self):
        self.version = 1
        self.width = 61
        self.height = 15
        self.data = bytearray(b'\x42'*(self.width * self.height))

    @staticmethod
    def __magic():
        return b'cIMG'

    def save(self, filename):
        with open(filename, 'wb') as f:
            f.write(CImgFile.__magic())
            f.write(int.to_bytes(self.version, 2, 'little'))
            f.write(int.to_bytes(self.width, 2, 'little'))
            f.write(int.to_bytes(self.height, 2, 'little'))
            f.write(self.data)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    CImgFile().save(sys.argv[1])
