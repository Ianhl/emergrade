# -*- coding: utf-8 -*-
"""
Simple Muse to Medical EEG Format
"""

import numpy as np
from pylsl import StreamInlet, resolve_byprop

MEDICAL_CHANNELS = ['Fp1', 'Fp2', 'F3', 'F4', 'F7', 'F8', 'T3', 'T4', 
                   'C3', 'C4', 'T5', 'T6', 'P3', 'P4', 'O1', 'O2', 
                   'Fz', 'Cz', 'Pz']

def simulate_medical_channels(muse_data):
    """Simple simulation of 19 channels from 4 Muse channels"""
    ch0, ch1, ch2, ch3 = muse_data
    
    # Add some variation to simulate different channels
    simulated = []
    for i in range(19):
        # Different weights for different channel types
        if i < 2:  # Fp1, Fp2 - direct measurements
            weight = [0, 1.0, 1.0, 0][i]
        elif i < 6:  # Frontal channels
            weight = [0.3, 0.7, 0.7, 0.3][i % 4]
        else:  # Other channels
            weight = [0.5, 0.4, 0.4, 0.5][i % 4]
        
        # Combine channels with some noise for realism
        base_value = (ch0 + ch1 + ch2 + ch3) / 4
        simulated.append(base_value * (0.8 + 0.4 * np.random.random()))
    
    return np.array(simulated)

if __name__ == "__main__":
    print('Looking for an EEG stream...')
    streams = resolve_byprop('type', 'EEG', timeout=2)
    if len(streams) == 0:
        raise RuntimeError('Can\'t find EEG stream.')

    print("Start acquiring data")
    inlet = StreamInlet(streams[0], max_chunklen=12)
    
    print('Medical EEG format - 19 channels:')
    print(','.join(MEDICAL_CHANNELS))

    sample_count = 0
    try:
        while True:
            eeg_data, timestamp = inlet.pull_chunk(timeout=0.1, max_samples=1)
            
            if len(eeg_data) > 0 and len(eeg_data[0]) == 4:
                raw_sample = np.array(eeg_data[0])
                medical_data = simulate_medical_channels(raw_sample)
                
                sample_count += 1
                formatted_values = [f"{val:.6f}" for val in medical_data]
                print(f"{sample_count}," + ",".join(formatted_values))

    except KeyboardInterrupt:
        print(f'\nClosing! Collected {sample_count} samples')