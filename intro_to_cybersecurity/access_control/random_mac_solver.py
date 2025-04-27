import re

from pwn import *

def parse_categories(c, categories):
    result = 0

    if len(c.strip()) == 0:
        return result

    to_parse = c.split(b',')
    for cat in to_parse:
        result |= categories[cat.strip()]

    return result

def is_subset_equal(a, b):
    return (b | a) == b

io = process(['/challenge/run'])

levels = {}
categories = {}

number_of_questions = io.recvregex(br'.+your goal is to answer (\d+) questions correctly.+:\n', capture=True).group(1)
number_of_questions = int(number_of_questions, 10)

number_of_levels = io.recvregex(br'(\d+) Levels.+:\n', capture=True).group(1)
number_of_levels = int(number_of_levels, 10)

for n in range(number_of_levels, 0, -1):
    level_name = io.readline().strip()
    levels[level_name] = n

number_of_categories = io.recvregex(br'(\d+) Categories:\n', capture=True).group(1)
number_of_categories = int(number_of_categories, 10)

for n in range(number_of_categories):
    category_name = io.readline().strip()
    categories[category_name] = 1 << n

r = re.compile(br'Q \d+. Can a Subject with level (.+) and categories \{(.*)\} (.+) an Object with level (.+) and categories \{(.*)\}\?\n') 

for n in range(number_of_questions):
    line = io.recvline()

    m = r.search(line)

    subject_level = levels[m.group(1)]
    subject_set = parse_categories(m.group(2), categories)

    is_read = m.group(3) == b'read'

    object_level = levels[m.group(4)]
    object_set = parse_categories(m.group(5), categories)

    is_allowed_by_level = subject_level >= object_level if is_read else object_level >= subject_level
    is_allowed = False

    if is_allowed_by_level:
        if is_read:
            is_allowed = is_subset_equal(object_set, subject_set)
        else:
            is_allowed = is_subset_equal(subject_set, object_set)

    if is_allowed:
        io.sendline(b'yes')
    else:
        io.sendline(b'no')

    io.recvline()

flag = io.recvregex(br'.+your flag:\n(.+)\n', capture=True).group(1).decode()
print(flag)
