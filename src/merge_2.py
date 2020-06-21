import json as js
import sys

final = {}
num_worker = int(sys.argv[1])
mtlyer = 1500/num_worker
mode = 'median'
for i in range(num_worker):
    file_name = '{}_{}_{}.json'.format(int(1+i*mtlyer), int(1+(i+1)*mtlyer), mode)
    print(file_name)
    with open(file_name) as input_file:
        final = {**final, **js.load(input_file)}

with open(f'{sys.argv[2]}', 'w', encoding='utf-8') as json_file:
    js.dump(final, json_file)