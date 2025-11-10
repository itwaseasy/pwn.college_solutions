import sys

class CImgFile:

    def __init__(self):
        self.version = 3
        self.width = 0 
        self.height = 0
        self.remaining_directives = 0


    def __header(self):
        return b'cIMG' + \
                int.to_bytes(self.version, 2, 'little') + \
                int.to_bytes(self.width, 1, 'little') + \
                int.to_bytes(self.height, 1, 'little') + \
                int.to_bytes(self.remaining_directives, 4, 'little')

    def load(self, filename):
        with open(filename, 'rb') as f:
            block_size = 10
            data = []

            # skip header
            f.read(len(self.__header()))

            while block := f.read(block_size):
                data.append((block[2], block[3], block[9]))

            x_coords, y_coords, _ = zip(*data)
            min_x = min(x_coords)
            max_x = max(x_coords)
            min_y = min(y_coords)
            max_y = max(y_coords)

            width = max_x - min_x + 1
            height = max_y - min_y + 1

            grid = [[' ' for _ in range(width)] for _ in range(height)]
            for x, y, char in data:
                row = y - min_y
                col = x - min_x

                grid[row][col] = chr(char)

            for row in grid:
                print("".join(row))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    f = CImgFile()
    f.load(sys.argv[1])
