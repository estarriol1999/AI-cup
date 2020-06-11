import numpy as np
import json as js

def postprocess(output_name, raw):
    dict_data = {i+1 : raw[i] for i in range(0, len(raw))}
    with open(output_name, 'w', encoding='utf-8') as json_file:
        js.dump(dict_data, json_file)
