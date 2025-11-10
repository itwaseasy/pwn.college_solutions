import sys

class CImgFile:
    def __init__(self):
        self.data = bytearray(b'\x7b\x6e\x6d\x36')

    def save(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.data)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    CImgFile().save(sys.argv[1])
