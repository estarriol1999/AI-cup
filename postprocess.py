import numpy as np
import json as js

raw = np.load('predict_all.npy', allow_pickle=True)
dict_data = {i+1 : raw[i] for i in range(0, len(raw))}


with open('upload.json', 'w', encoding='utf-8') as j:
    js.dump(dict_data, j)
