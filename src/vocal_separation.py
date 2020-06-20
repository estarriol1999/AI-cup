# Code source: Brian McFee
# License: ISC

from __future__ import print_function
import numpy as np
import json
import librosa
import sys
import os

import librosa.display

def vocal_separartion(wav_path):
    #############################################
    # Load an example with vocals.
    y, sr = librosa.load(wav_path, sr=None)
    
    # And compute the spectrogram magnitude and phase
    S_full, phase = librosa.magphase(librosa.stft(y))

    ###########################################################
    # The wiggly lines above are due to the vocal component.
    # Our goal is to separate them from the accompanying
    # instrumentation.
    #

    # We'll compare frames using cosine similarity, and aggregate similar frames
    # by taking their (per-frequency) median value.
    #
    # To avoid being biased by local continuity, we constrain similar frames to be
    # separated by at least 2 seconds.
    #
    # This suppresses sparse/non-repetetitive deviations from the average spectrum,
    # and works well to discard vocal elements.

    S_filter = librosa.decompose.nn_filter(S_full,
                                           aggregate=np.median,
                                           metric='cosine',
                                           width=int(librosa.time_to_frames(2, sr=sr)))

    # The output of the filter shouldn't be greater than the input
    # if we assume signals are additive.  Taking the pointwise minimium
    # with the input spectrum forces this.
    S_filter = np.minimum(S_full, S_filter)


    ##############################################
    # The raw filter output can be used as a mask,
    # but it sounds better if we use soft-masking.

    # We can also use a margin to reduce bleed between the vocals and instrumentation masks.
    # Note: the margins need not be equal for foreground and background separation
    margin_i, margin_v = 2, 10
    power = 2

    mask_i = librosa.util.softmask(S_filter,
                                   margin_i * (S_full - S_filter),
                                   power=power)

    mask_v = librosa.util.softmask(S_full - S_filter,
                                   margin_v * S_filter,
                                   power=power)

    # Once we have the masks, simply multiply them with the input spectrum
    # to separate the components

    S_foreground = mask_v * S_full
    S_background = mask_i * S_full
  
    tmp = librosa.core.istft(S_foreground)

    return tmp

if __name__ == '__main__':
    wav_dir = sys.argv[1]
    output_dir = sys.argv[2]
    begin = int(sys.argv[3])
    end = int(sys.argv[4])
    for song_num in range(begin, end):
        wav_path = os.path.join(wav_dir, f'{song_num}.wav')
        if not os.path.isfile(wav_path):
            print(f'{song_num}-th song not found')
            vocal = []
            continue
        vocal =  np.around(vocal_separartion(wav_path), 3).tolist()
        print(f'{song_num}-th song done')

        output_path = os.path.join(output_dir, f'{song_num}.json')
        with open(output_path, 'w') as json_file:
            json.dump(vocal, json_file)
