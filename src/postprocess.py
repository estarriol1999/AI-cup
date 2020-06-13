import numpy as np
import json as js

def postprocess(output_name, raw):
    notes = {}
    for song in raw:
        notes[song[0]] = song[1]
    with open(f'{output_name}.json', 'w', encoding='utf-8') as json_file:
        js.dump(notes, json_file)

