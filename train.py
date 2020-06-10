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

class Myrnn(nn.Module):
    def __init__(self, input_dim, hidden_size):
        super(Myrnn, self).__init__()
        self.hidden_size = hidden_size

        self.Linear1 = nn.Linear(input_dim, hidden_size)
        self.lstm = nn.LSTM(hidden_size, hidden_size, num_layers= 5, bidirectional= True)
        self.Linear2 = nn.Linear(hidden_size * 2, 2)
        self.Linear3 = nn.Linear(hidden_size * 2, 1)

    def forward(self, input_data):
        out = F.relu(self.Linear1(input_data))
        out, hidden = self.lstm(out)
        #out1 is for onset & offset
        out1 = torch.sigmoid(self.Linear2(out))
        #out2 is for pitch
        out2 = self.Linear3(out)
        return out1, out2

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

def collate_fn(samples):
    batch = {}
    #print (samples[0]['data'].shape)
    temp= [torch.from_numpy(np.array(sample['data'], dtype= np.float32)) for sample in samples]
    padded_data = rnn_utils.pad_sequence(temp, batch_first=True, padding_value= 0)
    batch['data']= padded_data
    batch['label']= [np.array(sample['label'], dtype= np.float32) for sample in samples]
    return batch

def do_training(net, loader, optimizer, device):

    num_epoch = 50
    criterion_onset= nn.BCELoss() #binary cross entropy
    criterion_pitch= nn.L1Loss()
    train_loss= 0.0
    total_length= 0

    for epoch in range(num_epoch):
        net.train()
        total_length= 0.0
        print ("epoch %d start time: %f" %(epoch, time.time()))
        train_loss= 0.0

        for batch_idx, sample in enumerate(loader):
            data = sample['data']
            data= torch.Tensor(data)

            target= sample['label']
            target= torch.Tensor(target)

            data= data.permute(1,0,2)
            target= target.permute(1,0,2)

            #print (data.shape)
            #print (target.shape)
            data_length= list(data.shape)[0]

            data = data.to(device, dtype=torch.float)
            target = target.to(device, dtype=torch.float)

            optimizer.zero_grad()
            output1, output2 = net(data)
            #print (output1)
            #print (output2)

            #print (output1.shape)
            #print (output2.shape)

            total_loss= criterion_onset(output1, torch.narrow(target, dim= 2, start= 0, length= 2))
            total_loss= total_loss+ criterion_pitch(output2, torch.narrow(target, dim= 2, start= 2, length= 1))
            train_loss= train_loss+ total_loss.item()
            total_length= total_length+ 1
            total_loss.backward()
            optimizer.step()

            if batch_idx % 50 == 0:
                print ("epoch %d, sample %d, loss %.6f" %(epoch, batch_idx, total_loss))
                #print ("current time: %f" %(time.time()))
                sys.stdin.flush()
        print('epoch %d, avg loss: %.6f' %(epoch, train_loss/ total_length))
        model_path= f'ori_{epoch}.pt'
        torch.save(net.state_dict(), model_path)
    return net

if __name__ == '__main__':
    print('Loading data ...')
    with open("train_all.pkl", 'rb') as pkl_file:
        train_data= pickle.load(pkl_file)

    input_dim= 23
    hidden_size= 50
    BATCH_SIZE= 1
    loader = Data.DataLoader(dataset=train_data, batch_size= BATCH_SIZE, shuffle=True, collate_fn=collate_fn)
    model = Myrnn(input_dim, hidden_size)
    optimizer = optim.Adam(model.parameters(), lr= 0.001)

    if torch.cuda.is_available():
        device = 'cuda'
    else: 
        device = 'cpu'
    print("use",device,"now!")

    model.to(device)
    model= do_training(model, loader, optimizer, device)