import sys
import os
import collections

class CImgFile:
    Sprite = collections.namedtuple('Sprite', ['id', 'height', 'width', 'data'])

    def __init__(self):
        self.version = 4
        self.width = 80 
        self.height = 1
        self.directives = {
                'load_data' : 0x01,
                'patch_data' : 0x02,
                'load_sprite': 0x03,
                'render_sprite': 0x04,
                'load_sprite_from_file': 0x05}
        self.remaining_directives = 0
        self.data = bytearray()

    def __header(self):
        return b'cIMG' + \
                int.to_bytes(self.version, 2, 'little') + \
                int.to_bytes(self.width, 1, 'little') + \
                int.to_bytes(self.height, 1, 'little') + \
                int.to_bytes(self.remaining_directives, 4, 'little')

    def __data(self):
        return self.data

    def generate_load_sprite_from_file_command(self, sprite, filename):
        FILENAME_SIZE = 255

        self.remaining_directives +=1
        self.data += int.to_bytes(self.directives['load_sprite_from_file'], 2, 'little') + \
            int.to_bytes(sprite.id, 1, 'little') + \
            int.to_bytes(sprite.width, 1, 'little') + \
            int.to_bytes(sprite.height, 1, 'little')

        self.data += filename.encode()
        self.data += b'\x00' * (FILENAME_SIZE - len(filename))

    def generate_render_sprite_instruction(self, sprite, rgb, x, y, repeat_x=1, repeat_y=1, stop=1):
        self.remaining_directives +=1
        self.data += int.to_bytes(self.directives['render_sprite'], 2, 'little') + \
                int.to_bytes(sprite.id, 1, 'little') + \
                rgb[0] + \
                rgb[1] + \
                rgb[2] + \
                int.to_bytes(x, 1, 'little') + \
                int.to_bytes(y, 1, 'little') + \
                int.to_bytes(repeat_x, 1, 'little') + \
                int.to_bytes(repeat_y, 1, 'little') + \
                int.to_bytes(stop, 1, 'little')

    def save(self, filename):
        flag_path = "/flag"

        self.width = os.path.getsize(flag_path) - 1
        sprite = self.Sprite(id=0, width=self.width, height=self.height, data=b'')

        self.generate_load_sprite_from_file_command(sprite, flag_path)
        self.generate_render_sprite_instruction(sprite, (b'\xff', b'\xff', b'\xff'), 0, 0)

        with open(filename, 'wb') as f:
            f.write(self.__header())
            f.write(self.__data())


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    f = CImgFile()
    f.save(f'{sys.argv[1]}')
