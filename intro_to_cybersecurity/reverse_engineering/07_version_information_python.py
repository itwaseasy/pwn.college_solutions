import sys

class CImgFile:
    @staticmethod
    def __header():
        return b'CONR'

    @staticmethod
    def __version():
        return 95

    def save(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.__header())
            f.write(int.to_bytes(self.__version(), 4, 'little'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    CImgFile().save(sys.argv[1])
