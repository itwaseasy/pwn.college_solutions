import sys
import struct
import collections

class CImgFile:
    Size = collections.namedtuple('Size', ['width', 'height'])

    def __init__(self):
        self.width = 80 
        self.data = bytearray()
        self.sprite_sizes = {}
        self.current_x = 0
        self.current_y = 0


    def __data(self):
        return self.data

    def proceed_load_sprite_command(self, pointer):
        COMMAND_SIZE = 3

        sprite_id, height, width = struct.unpack('<BBB', self.data[pointer:pointer+COMMAND_SIZE])
        pointer += COMMAND_SIZE + width*height

        self.sprite_sizes[sprite_id] = self.Size(width=width, height=height)

        return pointer

    def proceed_render_sprite_command(self, pointer):
        COMMAND_SIZE = 6

        sprite_id, r, g, b, _, _ = struct.unpack('<BBBBBB', self.data[pointer:pointer+COMMAND_SIZE])

        self.data[pointer:pointer+COMMAND_SIZE] = struct.pack('<BBBBBB', sprite_id, r, g, b, self.current_x, self.current_y)

        pointer += COMMAND_SIZE 

        sprite_size = self.sprite_sizes[sprite_id]

        if sprite_size.width + self.current_x >= self.width:
            self.current_x = 0
            self.current_y += sprite_size.height
        else:
            self.current_x += sprite_size.height


        return pointer

    def load(self, filename):
        HEADER_SIZE = 12

        with open(filename, 'rb') as f:
            self.data = bytearray(f.read())

        pointer = HEADER_SIZE

        while pointer < len(self.data):
            match self.data[pointer]:
                case 0x03:
                    pointer = self.proceed_load_sprite_command(pointer + 2)

                case 0x04:
                    pointer = self.proceed_render_sprite_command(pointer + 2)

                case _:
                    raise Exception("unsupported command")

    def save(self, filename):
        sprite_size = next(iter(self.sprite_sizes.values()))

        self.data[:8] = struct.pack('<4sHBB',
                                    b'cIMG', 3, self.width + sprite_size.width + 1, self.current_y + sprite_size.height + 1)

        with open(filename, 'wb') as f:
            f.write(self.__data())


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    f = CImgFile()
    f.load(sys.argv[1])
    f.save(f'{sys.argv[1]}_fixed.cimg')
