from pwn import *

def parse_categories(c, categories):
    result = 0

    if len(c.strip()) == 0:
        return result

    to_parse = c.split(",")
    for cat in to_parse:
        result |= categories[cat.strip()]

    return result

def is_subset_equal(a, b):
    return (b | a) == b

io = process(['/challenge/run'])

levels = {
        'TS': 4,
        'S': 3,
        'C': 2,
        'UC': 1}

categories = {
        'NUC': 1,
        'NATO': 1 << 1,
        'ACE': 1 << 2,
        'UFO': 1 << 3}

number_of_questions = io.recvregex(br'.+your goal is to answer (\d+) questions correctly.+:\n', capture=True).group(1)
number_of_questions = int(number_of_questions, 10)

for _ in range(number_of_questions):
    m = io.recvregex(br'Q \d+. Can a Subject with level (.+) and categories \{(.*)\} (.+) an Object with level (.+) and categories \{(.*)\}\?\n', capture=True)

    subject_level = levels[m.group(1).decode()]
    subject_set = parse_categories(m.group(2).decode(), categories)

    is_read = m.group(3).decode() == "read"

    object_level = levels[m.group(4).decode()]
    object_set = parse_categories(m.group(5).decode(), categories)

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

flag = io.recvregex(br'.+your flag:\n(.+)\n', capture=True).group(1).decode()
print(flag)
