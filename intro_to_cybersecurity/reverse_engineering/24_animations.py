import sys
import struct
import collections

class CImgFile:
    Size = collections.namedtuple('Size', ['width', 'height'])

    def __init__(self):
        self.width = 80 
        self.data = bytearray()
        self.commands = 0
        self.new_data = bytearray()


    def __data(self):
        return self.new_data

    def proceed_patch_command(self, pointer):
        COMMAND_SIZE = 4

        _, _, height, width = struct.unpack('<BBBB', self.data[pointer:pointer+COMMAND_SIZE])

        self.new_data += self.data[pointer:pointer+COMMAND_SIZE]
        pointer += COMMAND_SIZE

        for i in range(0, width*height, 4):
            _, _, _, char = struct.unpack('<BBBB', self.data[pointer:pointer+4])
            self.new_data[pointer:pointer+4] += struct.pack('<BBBB', 0xff, 0xff, 0xff, char)
            pointer += 4

        self.commands += 1

        return pointer

    def proceed_clear_command(self, pointer):
        COMMAND_SIZE = 1

        return pointer + COMMAND_SIZE

    def proceed_sleep_command(self, pointer):
        COMMAND_SIZE = 4

        return pointer + COMMAND_SIZE

    def load(self, filename):
        HEADER_SIZE = 12

        with open(filename, 'rb') as f:
            self.data = bytearray(f.read())

        pointer = HEADER_SIZE
        self.new_data += self.data[:pointer]

        while pointer < len(self.data):
            match self.data[pointer]:
                case 0x02:
                    self.new_data += self.data[pointer:pointer+2]
                    pointer = self.proceed_patch_command(pointer + 2)

                case 0x06:
                    pointer = self.proceed_clear_command(pointer + 2)

                case 0x07:
                    pointer = self.proceed_sleep_command(pointer + 2)

                case _:
                    raise Exception("unsupported command")

    def save(self, filename):
        self.new_data[8:12] = struct.pack('<I', self.commands)
        with open(filename, 'wb') as f:
            f.write(self.__data())


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    f = CImgFile()
    f.load(sys.argv[1])
    f.save(f'{sys.argv[1]}_fixed.cimg')
