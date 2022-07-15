#!/usr/bin/env python3

# Epochs objects are a data structure for representing and analyzing equal-duration chunks of the EEG/MEG signal. Epochs are
# most often used to represent data that is time-locked to repeated experimental events (such as stimulus onsets or subject button presses),
import mne
import json
import os
import os.path as op
import matplotlib.pyplot as plt
from pathlib import Path
import tempfile
import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt

#workaround for -- _tkinter.TclError: invalid command name ".!canvas"
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


import mne


# Current path
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


def epoch(param_meg,param_eeg,param_eog,param_ecg,param_emg,param_stim, event_id, raw, events, tmin, tmax):
    raw.pick_types(meg=param_meg,eeg=param_eeg,eog=param_eog,ecg=param_ecg,emg=param_emg, stim=param_stim).crop(tmax=60).load_data()

    report = mne.Report(title='Report')

    #raw
    report.add_raw(raw=raw, title='Raw', psd=False)  # omit PSD plot

    #events
    sfreq = raw.info['sfreq']
    report.add_events(events=events, title='Events', sfreq=sfreq)

    metadata, _, _ = mne.epochs.make_metadata(
        events=events,
        event_id=event_id,
        tmin=tmin,
        tmax=tmax,
        sfreq=raw.info['sfreq']
    )
    epochs = mne.Epochs(
        raw=raw, events=events, event_id=event_id, metadata=metadata
    )

    report.add_epochs(epochs=epochs, title='Epochs from "epochs"')

    # == SAVE REPORT ==
    report.save('out_dir_report/report.html', overwrite=True)

    # == SAVE FILE ==
    epochs.save(os.path.join('out_dir', 'meg-epo.fif'), overwrite=True)

def main():
    # Load inputs from config.json
    with open('config.json') as config_json:
        config = json.load(config_json)

    # Read the meg file
    data_file = config.pop('fif')

    # Read the event time
    tmin = config.pop('t_min')
    tmax = config.pop('t_max')

    # crop() the Raw data to save memory:
    raw = mne.io.read_raw_fif(data_file, verbose=False)

    # if 'events' in config.keys():
    #     events_file = config.pop('events')
    #     if op.exists(events_file):
    #         events = mne.read_events(events_file)
    #     else:
    #         events = mne.find_events(raw, stim_channel=config['stim_channel'])
    # else:
    #     events = mne.find_events(raw, stim_channel=config['stim_channel'])
    mask = 4096 + 256  # mask for excluding high order bits

    events = mne.find_events(raw, stim_channel=config['stim_channel'],
                             consecutive='increasing', mask=mask,
                             mask_type='not_and', min_duration=0.003)
    event_id_condition= config['event_id_condition']

    #Convert String to Dictionary using strip() and split() methods
    event_id = dict((x.strip(), int(y.strip()))
                     for x, y in (element.split('-')
                                  for element in  event_id_condition.split(', ')))

    id_list = list(event_id.values())

    events = mne.pick_events(events, include=id_list)

    print(config['param_eeg'])
    epochs = epoch(config['param_meg'],config['param_eeg'],config['param_eog'], config['param_ecg'],config['param_emg'],config['param_stim'], event_id, raw, events, tmin=tmin, tmax=tmax)

if __name__ == '__main__':
    main()
