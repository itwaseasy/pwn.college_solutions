import sys

class CImgFile:
    @staticmethod
    def __magic():
        return b'<mgE'

    @staticmethod
    def version():
        return 134

    def save(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.__magic())
            f.write(int.to_bytes(self.version(), 4, 'little'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    CImgFile().save(sys.argv[1])
