import json as js
import sys as sys

with open(sys.argv[1]) as upload:
    tmp = js.load(upload)

for i in range(1, 1501):
    if f'{i}' not in tmp:
        print(f'{i} miss !!')
