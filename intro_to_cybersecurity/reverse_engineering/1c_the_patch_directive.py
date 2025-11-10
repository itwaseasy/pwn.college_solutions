import sys
import os
import re
from collections import namedtuple

class CImgFile:
    Rectangle = namedtuple('Rectangle', ['x', 'y', 'width', 'height'])

    def __init__(self):
        self.version = 3
        self.width = 60
        self.height = 17
        self.directives = {
                'load_data' : 0x8636,
                'patch_data' : 0xa832}
        self.data = bytearray()
        self.ansi_data = []
        self.remaining_directives = 0


    def __header(self):
        return b'cIMG' + \
                int.to_bytes(self.version, 2, 'little') + \
                int.to_bytes(self.width, 1, 'little') + \
                int.to_bytes(self.height, 1, 'little') + \
                int.to_bytes(self.remaining_directives, 4, 'little')

    def __data(self):
        return self.data

    def get_pixel_segment(self, rectangle, data):
        segment = []

        for j in range(rectangle.height):
            current_row_y = rectangle.y + j
            start_index = (current_row_y * self.width) + rectangle.x
            end_index = start_index + rectangle.width

            if end_index > len(data):
                break

            segment.extend(data[start_index : end_index])

        return segment

    def generate_patch_instruction(self, rectangle, data):
        self.remaining_directives += 1
        self.data += int.to_bytes(self.directives['patch_data'], 2, 'little') + \
                int.to_bytes(rectangle.x, 1, 'little') + \
                int.to_bytes(rectangle.y, 1, 'little') + \
                int.to_bytes(rectangle.width, 1, 'little') + \
                int.to_bytes(rectangle.height, 1, 'little')

        self.data += b''.join([b''.join(x) for x in data])

    def generate_borders(self):
        borders = [
                self.Rectangle(x=0, y=0, width=self.width, height=1),
                self.Rectangle(x=0, y=self.height - 1, width=self.width, height=1),

                self.Rectangle(x=0, y=1, width=1, height=self.height - 1),
                self.Rectangle(x=self.width - 1, y=1, width=1, height=self.height - 1),
        ] 

        for b in borders:
            segment = self.get_pixel_segment(b, self.ansi_data)
            self.generate_patch_instruction(b, segment)

    def generate_text(self):
        num_rows = len(self.ansi_data) // self.width

        for y in range(1, num_rows - 1):
            # Get the 1D slice for the inner part of this row
            inner_row_start = (y * self.width) + 1
            inner_row_end = (y * self.width) + self.width - 1
            current_row_data = self.ansi_data[inner_row_start : inner_row_end]

            current_segment = []
            segment_start_x = -1

            for x_inner, value in enumerate(current_row_data):
                # Calculate the *global* x coordinate
                # It's the inner index + 1 (because we skipped col 0)
                global_x = x_inner + 1

                if value[3] != b' ':
                    if not current_segment:
                        # This is the start of a new segment
                        segment_start_x = global_x
                    current_segment.append(value)

                else:
                    if current_segment:
                        segment_width = len(current_segment)
                        rectangle = self.Rectangle(x=segment_start_x, y=y, width=segment_width, height=1)

                        self.generate_patch_instruction(rectangle, current_segment)

                        current_segment = []
                        segment_start_x = -1
        
        # If the row ended while we were in a segment
        if current_segment:
            segment_width = len(current_segment)
            rectangle = self.Rectangle(x=segment_start_x, y=y, width=segment_width, height=1)
            self.generate_patch_instruction(rectangle, current_segment)


    def load_ansi(self, filename):
        r = re.compile(br'.\[\d+;\d+;(\d+);(\d+);(\d+)m(.).+')

        with open(filename, 'rb') as f:
            while chr_line := f.read(24):
                m = r.search(chr_line)
                pixel = (
                        int(m.group(1)).to_bytes(1, 'little'),
                        int(m.group(2)).to_bytes(1, 'little'),
                        int(m.group(3)).to_bytes(1, 'little'),
                        m.group(4))
                self.ansi_data.append(pixel)


    def save(self, filename):
        self.generate_borders()
        self.generate_text()

        with open(filename, 'wb') as f:
            f.write(self.__header())
            f.write(self.__data())

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    f = CImgFile()
    f.load_ansi(f'{os.path.splitext(sys.argv[0])[0] + ".ansi"}')
    f.save(sys.argv[1])
