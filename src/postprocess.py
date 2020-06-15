import numpy as np
import json as js

def postprocess(output_name, raw):
    with open(output_name, 'w', encoding='utf-8') as json_file:
        js.dump(raw, json_file)

