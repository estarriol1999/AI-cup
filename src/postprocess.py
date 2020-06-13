import numpy as np
import json as js

def postprocess(output_name, raw):
    mean = {}
    median = {}
    mode = {}
    for song in raw:
        mean[song[0]] = song[1][0]
        median[song[0]] = song[1][1]
        mode[song[0]] = song[1][2]
    with open(f'{output_name}_mean.json', 'w', encoding='utf-8') as json_file:
        js.dump(mean, json_file)
    with open(f'{output_name}_median.json', 'w', encoding='utf-8') as json_file:
        js.dump(median, json_file)
    with open(f'{output_name}_mode.json', 'w', encoding='utf-8') as json_file:
        js.dump(mode, json_file)

