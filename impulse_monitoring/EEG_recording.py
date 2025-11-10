# -*- coding: utf-8 -*-
"""
Muse EEG Activity Tracker - CLI Session Manager (with Muselsl Integration)

This script now attempts to automatically start the 'muselsl stream' process
before connecting to the LSL stream, ensuring a self-contained CLI experience.
Now runs for a fixed duration of 90 seconds (1.5 minutes).
"""

from datetime import datetime
import numpy as np
from pylsl import StreamInlet, resolve_byprop
import utils
import csv
import time
import sys
import subprocess
import os

# --- Constants and Configuration ---
class Band:
    Delta = 0
    Theta = 1
    Alpha = 2
    Beta = 3
    Gamma = 4

BUFFER_LENGTH = 5
EPOCH_LENGTH = 1
OVERLAP_LENGTH = 0.8
SHIFT_LENGTH = EPOCH_LENGTH - OVERLAP_LENGTH
TIME_LIMIT_SECONDS = 60  # *** NEW: Fixed recording time of 1 minute ***

# Index of the channel(s) (electrodes) to be used
INDEX_CHANNEL = [0, 1, 2, 3] # Using all 4 channels
N_CHANNELS = len(INDEX_CHANNEL) # Calculate the required number of channels


def start_muselsl_stream():
    """Starts the 'muselsl stream' subprocess."""
    print("Attempting to start 'muselsl stream' process...")
    try:
        process = subprocess.Popen(
            ['muselsl', 'stream'],
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True
        )
        print("Waiting 10 seconds for Muse Bluetooth connection...")
        time.sleep(10)
        return process
    except FileNotFoundError:
        print("\nFATAL ERROR: 'muselsl' command not found. Please ensure 'muselsl' is installed.")
        return None
    except Exception as e:
        print(f"\nFATAL ERROR starting muselsl stream: {e}")
        return None


def connect_to_stream():
    """ Connects to the LSL EEG stream. """
    print('Looking for an EEG stream (LSL)...')
    streams = resolve_byprop('type', 'EEG', timeout=5)
    
    if len(streams) == 0:
        raise RuntimeError('Can\'t find LSL EEG stream. Muse-LSL failed to start or connect.')

    print(f"Successfully found EEG stream. Starting acquisition for {N_CHANNELS} channels.")
    inlet = StreamInlet(streams[0], max_chunklen=12)
    inlet.time_correction()
    fs = int(inlet.info().nominal_srate())

    return inlet, fs


def record_session(inlet, fs):
    """ The main recording loop that pulls data and writes to CSV. """
    
    eeg_buffer = np.zeros((int(fs * BUFFER_LENGTH), N_CHANNELS))
    filter_state = None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"eeg_session_{timestamp}.csv"

    bands = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']
    ch_names = [f'Ch{i+1}' for i in INDEX_CHANNEL]
    header = ['Timestamp'] + [f'{band}_{ch}' for band in bands for ch in ch_names]

    with open(csv_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(header)

    print(f'*** Recording started! Data is being saved to {csv_filename} ***')
    print(f'*** Session will run for a fixed {TIME_LIMIT_SECONDS} seconds. ***')

    start_time = time.time()
    try:
        while (time.time() - start_time) < TIME_LIMIT_SECONDS:
            
            # --- 3.1 ACQUIRE DATA ---
            eeg_data, timestamp = inlet.pull_chunk(
                timeout=1, max_samples=int(SHIFT_LENGTH * fs))

            if not eeg_data:
                continue

            ch_data = np.array(eeg_data)[:, INDEX_CHANNEL]
            eeg_buffer, filter_state = utils.update_buffer(
                eeg_buffer, ch_data, notch=True,
                filter_state=filter_state)

            # --- 3.2 COMPUTE BAND POWERS ---
            data_epoch = utils.get_last_data(eeg_buffer, EPOCH_LENGTH * fs)
            band_powers = utils.compute_band_powers(data_epoch, fs)

            avg_alpha = np.mean(band_powers[Band.Alpha * N_CHANNELS : (Band.Alpha + 1) * N_CHANNELS])
            avg_beta = np.mean(band_powers[Band.Beta * N_CHANNELS : (Band.Beta + 1) * N_CHANNELS])
            
            print(f"Time: {time.time() - start_time:.1f}s / {TIME_LIMIT_SECONDS}s | Alpha={avg_alpha:.2f}, Beta={avg_beta:.2f}")

            with open(csv_filename, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                row = [datetime.now().strftime('%H:%M:%S.%f')] + band_powers.tolist()
                csv_writer.writerow(row)

        print(f'\n*** Time limit ({TIME_LIMIT_SECONDS}s) reached. Recording finished. ***')
        return csv_filename

    except KeyboardInterrupt:
        print(f'\n*** Recording stopped by user. Data saved to {csv_filename} ***')
        return csv_filename
    except Exception as e:
        print(f"\nAn error occurred during recording: {e}")
        return None


def main_session():
    """ Manages the full lifecycle: start muselsl, connect, record, clean up. """
    muselsl_process = None
    try:
        # 1. Start muselsl stream
        muselsl_process = start_muselsl_stream()
        if not muselsl_process:
            return

        # 3. Connect to LSL stream
        inlet, fs = connect_to_stream()

        # 4. Record
        session_file = record_session(inlet, fs)

        if session_file:
            print(f"\nSession file generated: {session_file}")

    except RuntimeError as e:
        print(f"Fatal Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # 5. Terminate muselsl process
        if muselsl_process and muselsl_process.poll() is None:
            print('\nAttempting to terminate muselsl stream process...')
            muselsl_process.terminate()
            muselsl_process.wait()
            print('Muselsl stream process terminated.')
        print('Exiting EEG session manager.')


if __name__ == "__main__":
    main_session()