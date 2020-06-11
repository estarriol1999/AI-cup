import json
import os
import numpy as np
import pickle
import sys
import time

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data as Data
import torch.nn.utils.rnn as rnn_utils

class MyData(Data.Dataset):
    def __init__(self, data_seq, label):
        self.data_seq = data_seq
        self.label= label

    def __len__(self):
        return len(self.data_seq)

    def __getitem__(self, idx):
        return {
            'data': self.data_seq[idx],
            'label': self.label[idx]
        }

if __name__ == '__main__':

    THE_FOLDER = "./MIR-ST500"

    data_seq= []
    label= []
    
    for the_dir in os.listdir(THE_FOLDER):
        #print (the_dir)
        if not os.path.isdir(THE_FOLDER + "/" + the_dir):
            continue

        json_path = THE_FOLDER + "/" + the_dir+ f"/{the_dir}_feature.json"
        #gt_path= THE_FOLDER+ "/" +the_dir+ "/"+ the_dir+ "_groundtruth.txt"

        #youtube_link_path= THE_FOLDER+ "/" + the_dir+ "/"+ the_dir+ "_link.txt"

        with open(json_path, 'r') as json_file:
            temp = json.loads(json_file.read())
        temp.pop("chroma_1")
        temp.pop("chroma_2")
        temp.pop("chroma_3")
        temp.pop("chroma_4")
        temp.pop("chroma_5")
        temp.pop("chroma_6")
        temp.pop("chroma_7")
        temp.pop("chroma_8")
        temp.pop("chroma_9")
        temp.pop("chroma_10")
        temp.pop("chroma_11")
        temp.pop("chroma_12")
        #gtdata = np.loadtxt(gt_path)

        data= []
        for key, value in temp.items():
            data.append(value)

        data= np.array(data).T

        data_seq.append(data)
        #label.append(gtdata)
    
    #label= preprocess(data_seq, label)
    train_data = MyData(data_seq, label)
    
    
    
    with open("feature_500_pickle.pkl", 'wb') as pkl_file:
        pickle.dump(train_data, pkl_file)
