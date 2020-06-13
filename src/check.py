import json as js

with open(f'upload.json') as upload:
    tmp = js.load(upload)

for i in range(1, 1501):
    if f'{i}' not in tmp:
        print(f'{i} miss !!')
