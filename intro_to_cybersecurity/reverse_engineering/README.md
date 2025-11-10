
# "Reverse Engineering" from the "Intro to Cybersecurity" course by pwn.college

Continuing my journey with pwn.college challenges, this is the RE part from the "intro" course. It's funny that when I first stumbled upon pwn.college, it didn't exist yet, so I first solved the RE assignment from the "Program Security" course. And I must say, I liked them even more because they were essentially about reverse engineering. That course is also quite good, but it's more of a development exercise than a true reverse engineering course.

My main takeaway is that drawing ANSI/ASCII art was and remains incredibly fun!

All tasks are built on a custom file format, cIMG, which you'll need to learn and understand to correctly generate your own files. Typically, a task provides you with a binary file, which is an "image processor" that reads and renders data from the cIMG file you've prepared. Progressing from creating simple headers, you'll eventually move on to working with animated sprites and, finally, see a "game" built on this format, which is truly awesome.

It's very convenient that you'll also get part of the source code along with the binary file itself. All the type definitions (again, usually) are already there, so you won't have to spend a lot of time rebuilding the entire format from scratch. Simply pass the definitions to IDA, and it will generate quite readable decompiled source code.

I'll skip most of the tasks, as they're fairly trivial, and only cover the ones that are challenging. If you need the previous ones, just check the link with all the sources at the end. However, as always, please only use it if you're truly struggling, as the primary goal is to teach you, not to provide an answer you can copy and paste and tweet on X that you solved it yourself.

## 0x18: internal state

This is the first "real" cIMG file you'll need to generate, as the previous tasks were primarily focused on preparation. The basic idea is that the `cimg` binary contains a `desired_output` with the required image, which you need to generate within the file. The main problem is that it already contains ANSI-encoded data, and your cIMG file only needs to contain the correct header and the required number of (r,g,b,char) tuples representing the desired image.

My approach to solving this and subsequent problems is to write the `desired_output` data to a separate `.ansi` file and then load and parse it during image generation.

## 0x1a: file formats directives

This task introduces the third version of the cIMG format and the concept of "directives." While previously you'd dump all the necessary data immediately after the header, now the file consists of a header and a set of "directives" that tell the `cimg` processor what to do. Each directive (there will be seven more) has its own format and number of "parameters," ranging from a simple byte to a complex nine-field structure for the `render_sprite` directive.

## 0x1c: the patch directive

This is the new `patch` directive, which renders a "sprite," or, more simply, replaces the rectangular data in the framebuffer with the data you provide. This task is also very sensitive to the size of the generated file, so you won't be able to use the `load_data` directive as before.

My approach is this: given that the framebuffer initially contains the tuples (255, 255, 255, ' '), I don't need to rewrite them, since the resulting `desired_data` already contains them too. I only need to "draw" the borders and the text inside.

The borders are fairly simple, since the coordinates are known. The text itself is a bit confusing, so my solution is to find non-empty "segments" in the image (parts that don't contain spaces) and use the `patch` directive with their coordinates to write them to the framebuffer.

## 0x1d: optimizing for space

Now the `cimg` binary is even more strict about the file size, so the previous solution doesn't work because the generated file is larger than necessary.

The approach is the same: generating borders and forming inner text. However, the segment separator is now two adjusted spaces instead of a single space. This essentially "truncates" more data into a single line and generates fewer patch directives, reducing the file size.

## 0x1e: tweaking images

This is a slightly different exercise: now you need to read a cIMG file and properly "extract" data from it, rather than generate it. The task creates a file with an embedded flag, but the problem is that each `patch` directive used displays the data in (1,1) coordinates. Therefore, attempting to render this file with the `cimg` binary will only show the last character of the flag, as all previous characters will be overwritten.

My approach is to parse the file, read each `patch` directive, and save the data it has. Given that the data is a "figlet," it cannot be printed simply. Each part also needs to be correctly rendered in the correct coordinates on the terminal.

## 0x1f: storage and retrieval

This task introduces two new directives for loading and rendering sprites. On the one hand, this will make your life much easier, as you no longer need to patch the framebuffer: you can load a sprite once and draw it multiple times at any coordinates. On the other hand, the `cimg` executable expects you to generate an even smaller file size than before.

The approach remains the same as before: I render the borders first, and then the text. For the borders, you only need two sprites: a horizontal and a vertical line, and you can draw each of them twice.

However, the text becomes quite complex: the previous line-by-line approach is ineffective, as it requires multiple loading/rendering instructions. Therefore, the idea is to "cut" the entire drawn character, not just some line. The algorithm uses the classic BFS approach to detect character boundaries and save them as a sprite.

## 0x20: extracting knowledge

This is similar to "tweaking images": you need to parse the file, not generate it. On top of that, the file is "broken" somehow, and now it contains sprites. Therefore, unless you want to write a full-fledged ASCII renderer, it's better to "patch" the generated file and let the `cimg` executable render it.

There are two problems with the file: each `render_sprite` directive has coordinates of (0,0), and the header contains incorrect width and height values. You need to find a way to render each sprite at the correct coordinates and correctly calculate the framebuffer size.

## 0x21: advanced sprites

I would say this is the hardest challenge of the whole series: you need to generate a file with the same "picture" as in the "storage and retrieval" challenge, but the length of the resulting file should not exceed 285 bytes.

The task also introduces version 4 of the cIMG format: the `render_sprite` directive has been modified and now contains three additional fields that allow the same sprite to be rendered multiple times horizontally and/or vertically, literally by copying and pasting it. Furthermore, the directive allows partial rendering, so it contains what I've called a "stop symbol": the rendering process stops upon encountering this symbol.

The previous solution, of course, doesn't work because it creates larger files. First, the borders occupy almost half the file, so they need to be optimized in some way. My solution is as follows:

- generate a line of dots from above
- generate a line of apersands at the bottom
- generate a square from horizontal lines (top to bottom), leaving 1 dot and 1 ampersand in each corner
- generate a square from vertical lines (top to bottom), leaving 1 dot and 1 ampersand in each corner
- fill the inner square with spaces

This requires only five load instructions, where the sprite data consists of just one character, and five render instructions, significantly reducing the final file size.

Unfortunately, this wasn't enough, so I had to fix the text generation algorithm. Funnily enough, it had a small bug: it was generating five sprites from four letters. Once I fixed it, the final size was exactly 285 bytes.

I suppose the original intention of the task was to utilize the "stop symbol" in some way, but that would have required me to change the entire text rendering logic, so I decided to leave it as is.

## 0x22: accessing resources

The task introduces a new `load_sprite_from_file` directive, which allows the data to be saved to disk rather than in the image itself.

But that's not the point. Given that the `cimg` binary has the setuid bit enabled, it can essentially read any file, including the flag itself. So the idea is to load the "sprite" data from the `/flag` file and render it correctly.

## 0x23: unsafe animations

Another new directive is `clear`, which clears the screen. The problem is that it uses `system("clear")`, which allows you to create your own `clear` command and place it in your within your `PATH`.

So the solution is to generate a proper `cat /flag` script and run `cimg` with a modified `PATH` env variable and the appropriate image file that executes it.

## 0x24: animations

This task introduces the final directives for properly animating sprites and provides a file that doesn't implement them correctly. You need to either fix it or extract the data and render it yourself.

I decided to fix this by removing all the clear/sleep directives, leaving only `patch`, so the resulting image has a static flag inside.

## 0x25 - 0x27: basic patching skills

The last three challenges are relatively simple compared to the previous ones: you simply need to locate the correct place in the executable file and apply the patch. The process is quite tedious, but the game you're playing in the end is very cool, so have fun!

The challenges can be found [here](https://pwn.college/intro-to-cybersecurity/), and my solutions are [here](https://github.com/itwaseasy/pwn.college_solutions/tree/master/intro_to_cybersecurity/reverse_engineering).
