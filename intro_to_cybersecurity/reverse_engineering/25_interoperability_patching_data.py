import sys
import hashlib

class CImgFile:
    ORIGINAL_SHA256 = '8350177220ae4f2ccca9ad31fd1c25d7027810b616b1dbd1c3ceabf74a4e274f'

    def __init__(self):
        self.data = bytearray()

    def __data(self):
        return self.data

    def patch(self):
        offset = 0x32f9

        self.data[offset:offset+4] = b'CNNR'

    def load(self, filename):
        with open(filename, 'rb') as f:
            self.data = bytearray(f.read())

        h = hashlib.sha256(self.data).hexdigest()
        if h != self.ORIGINAL_SHA256:
            raise Exception("wrong sha256")

    def save(self, filename):
        self.patch()

        with open(filename, 'wb') as f:
            f.write(self.__data())

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    f = CImgFile()
    f.load(f'{sys.argv[1]}')
    f.save(f'{sys.argv[1]}.patched')
