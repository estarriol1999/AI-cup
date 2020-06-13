import json as js
import sys as sys


final = {}

for file_name in sys.argv[1:-1]:
    print(file_name)
    with open(file_name) as input_file:
        final = {**final, **js.load(input_file)}
    print(len(final.keys()))


with open(f'{sys.argv[-1]}', 'w', encoding='utf-8') as json_file:
    js.dump(final, json_file)
