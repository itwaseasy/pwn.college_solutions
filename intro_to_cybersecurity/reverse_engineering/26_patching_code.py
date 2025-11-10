import sys
import hashlib

class CImgFile:
    ORIGINAL_SHA256 = '7b1d836d30a4f9da28cca9259f5d42b7420ceec9b0d330377dcd406be993be17'

    def __init__(self):
        self.data = bytearray()

    def __data(self):
        return self.data

    def patch(self):
        magic_offset = 0x32f9
        case_offsets = [0x13ed, 0x13fd, 0x140d, 0x141d, 0x142d, 0x1440, 0x1453]

        self.data[magic_offset:magic_offset+4] = b'CNNR'

        for i in range(len(case_offsets)):
            offset = case_offsets[i]
            self.data[offset:offset+1] = int.to_bytes(len(case_offsets) - i, 1, 'little')

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
