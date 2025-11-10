import sys
import os
import re
import collections

class CImgFile:
    Rectangle = collections.namedtuple('Rectangle', ['x', 'y', 'width', 'height'])
    Sprite = collections.namedtuple('Sprite', ['id', 'height', 'width', 'data'])

    def __init__(self):
        self.version = 4
        self.width = 76 
        self.height = 24
        self.directives = {
                'load_data' : 0x01,
                'patch_data' : 0x02,
                'load_sprite': 0x03,
                'render_sprite': 0x04}
        self.data = bytearray()
        self.ansi_data = []
        self.remaining_directives = 0
        self.sprite_id = 0


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

            segment.extend(item[3] for item in data[start_index : end_index])

        return segment

    def generate_load_sprite_instruction(self, sprite):
        self.remaining_directives +=1
        self.data += int.to_bytes(self.directives['load_sprite'], 2, 'little') + \
                int.to_bytes(sprite.id, 1, 'little') + \
                int.to_bytes(sprite.width, 1, 'little') + \
                int.to_bytes(sprite.height, 1, 'little')

        self.data += b''.join(sprite.data)

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


    def create_sprite(self, rectangle):
        data = self.get_pixel_segment(rectangle, self.ansi_data)
        sprite = self.Sprite(id=self.sprite_id, width=rectangle.width, height=rectangle.height, data=data)

        self.sprite_id +=1
        return sprite

    def generate_borders(self):
        horizontal = self.create_sprite(
                self.Rectangle(x=1, y=0, width=1, height=1))

        vertical = self.create_sprite(
                self.Rectangle(x=0, y=1, width=1, height=1))

        dot = self.create_sprite(
                self.Rectangle(x=0, y=0, width=1, height=1))

        ap = self.create_sprite(
                self.Rectangle(x=0, y=self.height-1, width=1, height=1))

        space = self.create_sprite(
                self.Rectangle(x=1, y=1, width=1, height=1))


        self.generate_load_sprite_instruction(horizontal)
        self.generate_load_sprite_instruction(dot)
        self.generate_load_sprite_instruction(ap)
        self.generate_load_sprite_instruction(vertical)
        self.generate_load_sprite_instruction(space)


        self.generate_render_sprite_instruction(dot, (b'\xff',b'\xff',b'\xff'), 0, 0, self.width, 1)
        self.generate_render_sprite_instruction(ap, (b'\xff',b'\xff',b'\xff'), 0, self.height-1, self.width, 1)
        self.generate_render_sprite_instruction(horizontal, (b'\xff',b'\xff',b'\xff'), 1, 0, self.width-2, self.height)
        self.generate_render_sprite_instruction(vertical, (b'\xff',b'\xff',b'\xff'), 0, 1, self.width, self.height-2)
        self.generate_render_sprite_instruction(space, (b'\xff',b'\xff',b'\xff'), 1, 1, self.width-2, self.height-2)

    def find_text_rects(self, data_1d, width, height, min_spaces_sep=1):
        # Convert 1D data to 2D grid for easy (y, x) access
        grid = []
        for y in range(height):
            grid.append(data_1d[y * width : (y + 1) * width])

        visited = [[False for _ in range(width)] for _ in range(height)]
        
        results = []

        for y in range(1, height - 1):
            for x in range(1, width - 1):
                
                (r, g, b, char) = grid[y][x]
                
                if char == b' ' or visited[y][x]:
                    continue
                    
                # found the start of a new blob
                target_color = (r, g, b)
                blob_coords = set()
                
                queue = collections.deque([(x, y)])
                visited[y][x] = True
                
                # run BFS to find all connected parts
                while queue:
                    cx, cy = queue.popleft()
                    blob_coords.add((cx, cy))
                    
                    # find all valid neighbors within the frame
                    neighbors_to_check = []

                    # Rule 3: Vertical Neighbors
                    neighbors_to_check.append((cx, cy - 1)) # up
                    neighbors_to_check.append((cx, cy + 1)) # down

                    neighbors_to_check.append((cx-1, cy - 1)) # up
                    neighbors_to_check.append((cx-1, cy + 1)) # down

                    # rule 2: horizontal neighbors (scan with space-skipping)
                    
                    # scan right (stop before the right frame)
                    space_count = 0
                    for nx in range(cx + 1, width - 1):
                        n_char = grid[cy][nx][3]
                        n_color = grid[cy][nx][0:3]
                        if n_char == b' ':
                            space_count += 1
                            if space_count >= min_spaces_sep: break
                        elif n_color == target_color:
                            neighbors_to_check.append((nx, cy)); break
                        else:
                            break # Hit different color

                    # scan left (stop before the left frame)
                    space_count = 0
                    for nx in range(cx - 1, 0, -1): # (stop at index 1)
                        n_char = grid[cy][nx][3]
                        n_color = grid[cy][nx][0:3]
                        if n_char == b' ':
                            space_count += 1
                            if space_count >= min_spaces_sep: break
                        elif n_color == target_color:
                            neighbors_to_check.append((nx, cy)); break
                        else:
                            break

                    # process all found neighbors
                    for nx, ny in neighbors_to_check:
                        
                        # check bounds (MUST be within the inner frame)
                        if 1 <= nx < (width - 1) and 1 <= ny < (height - 1):
                            if not visited[ny][nx]:
                                (nr, ng, nb, nchar) = grid[ny][nx]
                                if nchar != b' ' and (nr, ng, nb) == target_color:
                                    visited[ny][nx] = True
                                    queue.append((nx, ny))

                # BFS is done, calculate bounding box
                if not blob_coords:
                    continue
                    
                all_x = [c[0] for c in blob_coords]
                all_y = [c[1] for c in blob_coords]
                
                min_x, max_x = min(all_x), max(all_x)
                min_y, max_y = min(all_y), max(all_y)
                
                rect_width = (max_x - min_x) + 1
                rect_height = (max_y - min_y) + 1
                
                results.append((r, g, b, min_x, min_y, rect_width, rect_height))

        return results

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

        rects = self.find_text_rects(self.ansi_data, self.width, self.height, min_spaces_sep=3)

        for rect in rects:
            (r, g, b, x, y, width, height) = rect

            sprite = self.create_sprite(
                    self.Rectangle(x=x, y=y, width=width, height=height))

            self.generate_load_sprite_instruction(sprite)
            self.generate_render_sprite_instruction(sprite, (r,g,b), x, y)

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

