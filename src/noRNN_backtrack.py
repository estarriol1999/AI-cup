  
import argparse
import os
import sys
import librosa
import mido
import json
import numpy as np
from scipy import stats
import time

from madmom.audio.filters import LogarithmicFilterbank
from madmom.audio.filters import MelFilterbank
#from madmom.audio.filters import SimpleChromaFilterbank 
#from madmom.audio.filters import  HarmonicFilterbank
from madmom.features.onsets import SpectralOnsetProcessor
from madmom.features.onsets import RNNOnsetProcessor
from madmom.features.onsets import CNNOnsetProcessor
from madmom.audio.signal import normalize
from scipy import signal
from postprocess import postprocess
import subprocess

#subprocess.check_output('py noRNN.py ./wav-1500 ./testing ./output 1 1501')
MEAN = 1
MEDIAN = 2
MODE = 3

# ./multi_noRNN.sh /winux/AI-cup-data/wav-1500 /winux/AI-cup-data/AIcup_testset_ok /winux/AI-cup-data/spectral+0.02 1500 2
# python3 noRNN.py ./wav-1500 ./testing ./output 1002 1501 &
class Note:
    def __init__(self, frame, frame_pitch, onset_time, offset_time):
        self.frame_pitch = frame_pitch
        self.frame = frame
        self.onset_time = onset_time
        self.offset_time = offset_time
        self.pitch = 0
def get_onset(wav_path):
    y, sr = librosa.core.load(wav_path, sr= None)
    sos = signal.butter(25, 100, btype= 'highpass', fs= sr, output='sos')
    wav_data= signal.sosfilt(sos, y)
    wav_data= normalize(wav_data)

    sodf = SpectralOnsetProcessor(onset_method='spectral_flux', 
    fps= 50, 
    filterbank=LogarithmicFilterbank, 
    fmin= 100, 
    num_bands= 24, 
    norm= True)
    #sodf = CNNOnsetProcessor()
    #sodf = RNNOnsetProcessor()
    from madmom.audio.signal import Signal
    onset_strength= (sodf(Signal(data= wav_data, sample_rate= sr)))
    onset_strength= librosa.util.normalize(onset_strength)
    h_length= int(librosa.time_to_samples(1./50, sr=sr))
    onset_times= librosa.onset.onset_detect(onset_envelope= onset_strength,
                                      sr=sr,
                                      hop_length= h_length,
                                      backtrack=True,
                                      units='time', pre_max= 5, post_max= 5,
                                      pre_avg= 4, post_avg= 4, wait=1)
    return onset_times
def generate_notes(onset_times, ep_frames):
    notes = []
    onset_num= 0
    cur_frame= []
    cur_pitch= []
    for time, pitch in ep_frames:
        if (onset_num+ 1) < len(onset_times) and time > (onset_times[onset_num+ 1]- 0.016):
            note= Note(frame= cur_frame, frame_pitch= cur_pitch, onset_time= onset_times[onset_num]
                , offset_time= onset_times[onset_num+ 1])
            notes.append(note)
            
            cur_frame= []
            cur_pitch= []
            onset_num= onset_num+ 1
        if time > (onset_times[onset_num]- 0.016):
            cur_frame.append(time)
            cur_pitch.append(pitch)
    if cur_frame != []:
        note= Note(frame= cur_frame, frame_pitch= cur_pitch, onset_time= onset_times[onset_num]
            , offset_time= cur_frame[-1])
        notes.append(note)
        
    return notes
def get_note_level_pitch(notes, method):
    for note in notes:
        total= []
        for pitch in note.frame_pitch:
            if pitch > 0:
                total.append(pitch)
        if len(total) == 0:
            note.pitch= 0
        else:
            if method == MEDIAN :
                note.pitch = round(np.median(total), 0) 
            elif method == MODE:
                total = [round(i, 1) for i in total]
                note.pitch = round(stats.mode(total)[0][0], 0)
            elif method == MEAN:
                note.pitch = round(sum(total)/len(total), 0) 
    return notes
def get_offset(notes):
    for note in notes:
        if note.pitch != 0:
            offset= 0
            for i in range(len(note.frame_pitch)):
                if note.frame_pitch[i] > 0:
                    offset= i
            
            if offset > 2:
                note.offset_time= note.frame[offset]
    return notes
def notes2list(notes):
    result = []
    for note in notes:
        if note.pitch != 0:
            result.append([note.onset_time, note.offset_time, note.pitch])
    return result
def main(wav_path, pitch_path):
    
    ep_frames = json.load(open(pitch_path))
    onset_times = get_onset(wav_path)
    notes = generate_notes(onset_times, ep_frames)
    
    median_notes   = get_note_level_pitch(notes, MEDIAN)
    mode_notes   = get_note_level_pitch(notes, MODE)
    median_result = notes2list(median_notes)
    mode_result = notes2list(mode_notes)
    return median_result, mode_result 
if __name__ == '__main__':
    wav_dir = sys.argv[1]
    pitch_dir = sys.argv[2]
    output_dir = sys.argv[3]
    begin = int(sys.argv[4])
    end = int(sys.argv[5])
    median_raw = {} 
    mode_raw = {}
    for song_num in range(begin, end):
        wav_path = os.path.join(wav_dir, f'{song_num}.wav')
        pitch_path = os.path.join(pitch_dir, f'{song_num}', f'{song_num}_vocal.json')
        if not os.path.isfile(wav_path) or not os.path.isfile(pitch_path):
            print(f'{song_num}-th song not found')
            median_raw[song_num] = []
            mode_raw[song_num] = []
            continue
        
        median_result, mode_result = main(wav_path, pitch_path)
        median_raw[song_num] = median_result
        mode_raw[song_num] = mode_result 
        print(f'{song_num}-th song done')
    output_file_name = os.path.join(output_dir, f'{begin}_{end}_median.json')
    postprocess(output_file_name, median_raw)
    output_file_name = os.path.join(output_dir, f'{begin}_{end}_mode.json')
    postprocess(output_file_name, mode_raw)