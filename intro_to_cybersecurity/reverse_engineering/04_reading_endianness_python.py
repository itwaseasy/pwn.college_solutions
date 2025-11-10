import sys

class CImgFile:
    def __init__(self):
        self.data = bytearray(b'\x63\x6e\x7e\x52')

    def save(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.data)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    CImgFile().save(sys.argv[1])
