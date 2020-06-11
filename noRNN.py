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
from madmom.features.onsets import SpectralOnsetProcessor
from madmom.audio.signal import normalize
from scipy import signal

from postprocess import postprocess

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

    sodf = SpectralOnsetProcessor(onset_method='complex_flux', fps= 50, filterbank=LogarithmicFilterbank, fmin= 100, num_bands= 24, norm= True)
    from madmom.audio.signal import Signal
    onset_strength= (sodf(Signal(data= wav_data, sample_rate= sr)))
    onset_strength= librosa.util.normalize(onset_strength)
    h_length= int(librosa.time_to_samples(1./50, sr=sr))

    onset_times= librosa.onset.onset_detect(onset_envelope= onset_strength,
                                      sr=sr,
                                      hop_length= h_length,
                                      units='time', pre_max= 5, post_max= 5, 
                                      pre_avg= 5, post_avg= 5)

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

def get_note_level_pitch(notes):
    for note in notes:
        voiced_note= 0
        total= 0
        for i in range(len(note.frame_pitch)):
            if note.frame_pitch[i] > 0:
                voiced_note= voiced_note+ 1
                total= total+ note.frame_pitch[i]

        if voiced_note == 0:
            note.pitch= 0
        else:
            note.pitch= round( total / float(voiced_note) )

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
    #print ("start processing time: %f" %(time.time()))
    
    ep_frames = json.load(open(pitch_path))

    onset_times = get_onset(wav_path)
    notes = generate_notes(onset_times, ep_frames)
    notes = get_note_level_pitch(notes)
    notes = get_offset(notes)

    result = notes2list(notes)

    #print ("end processing time: %f" %(time.time()))
    
    return result


if __name__ == '__main__':
    wav_dir = sys.argv[1]
    pitch_dir = sys.argv[2]
    raw = []
    num = 0
    for song_dir in os.listdir(wav_dir):
        if num > 2: break
        song_num = song_dir.replace(f'.wav', '')
        wav_path = os.path.join(wav_dir, song_dir)
        pitch_path = os.path.join(pitch_dir, song_num, f'{song_num}_vocal.json')
        raw.append(main(wav_path, pitch_path))

        print(f'{num}-th done')
        num += 1

    postprocess(f'upload.json', raw)
