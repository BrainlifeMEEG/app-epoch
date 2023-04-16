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
import sys

#workaround for -- _tkinter.TclError: invalid command name ".!canvas"
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


import mne


# Current path
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


def epoch(param_meg,param_eeg,param_eog,param_ecg,param_emg,param_stim, plot_cond, pick, event_id, raw, events, tmin, tmax, metadata):
    raw.pick_types(meg=param_meg,eeg=param_eeg,eog=param_eog,ecg=param_ecg,emg=param_emg, stim=param_stim).load_data()

    report = mne.Report(title='Report')

    #raw
    #report.add_raw(raw=raw, title='Raw', psd=False)  # omit PSD plot

    #events
    sfreq = raw.info['sfreq']
    #report.add_events(events=events, title='Events', sfreq=sfreq)

    epochs = mne.Epochs(raw=raw, events=events, event_id=event_id, metadata=metadata, tmin=tmin, tmax=tmax)
    epochs = epochs['response_correct']
    report.add_epochs(epochs=epochs, title='Epochs from "epochs"')

    correct_response_count = metadata['response_correct'].sum()
    report.add_html('<dev>'+print(f'Correct responses: {correct_response_count}\n'
          f'Incorrect responses: {len(metadata) - correct_response_count}')+'</dev>')
    
    # == SAVE REPORT ==
    report.save('out_dir_report/report.html', overwrite=True)
    sys.stdout.write('test')

    # == SAVE FILE ==
    epochs.save(os.path.join('out_dir', 'meg-epo.fif'), overwrite=True)
    
    
    # == FIGURES ==
   #plt.figure(1)
    #fig_ep = epochs['auditory/left'].plot_image(picks='mag', combine='mean')
    #fig_ep.savefig(os.path.join('out_figs','epoimg.png'))
    
     # == FIGURES ==
    plt.figure(1)
    fig_ep = epochs[plot_cond].plot_image(picks=[pick])
    fig_ep[0].savefig(os.path.join('out_figs','epoimg.png'))


def main():
    # Load inputs from config.json
    with open('config.json') as config_json:
        config = json.load(config_json)

    # Read the meg file
    data_file = config.pop('fif')

    # Read the event time
    tmin = config.pop('tmin')
    tmax = config.pop('tmax')

    # crop() the Raw data to save memory:
    raw = mne.io.read_raw_fif(data_file, verbose=False)
    mask = 4096 + 256  # mask for excluding high order bits

    #if 'events' in config.keys():
    #    events_file = config.pop('events')
    #    if op.exists(events_file):
    #        events = mne.read_events(events_file)
    #    else:
    #        events = mne.find_events(raw, stim_channel=config['stim_channel'],
    #                         consecutive='increasing', mask=mask,
    #                         mask_type='not_and', min_duration=0.003)
    #else:
    #    events = mne.find_events(raw, stim_channel=config['stim_channel'],
    #                         consecutive='increasing', mask=mask,
    #                         mask_type='not_and', min_duration=0.003)
    

    events = mne.find_events(raw, stim_channel=config['stim_channel'],
                             consecutive='increasing', mask=mask,
                             mask_type='not_and', min_duration=0.003)
    event_id_condition= config['event_id_condition_mapping']

    #Convert String to Dictionary using strip() and split() methods
    event_id = dict((x.strip(), int(y.strip()))
                     for x, y in (element.split('-')
                                  for element in  event_id_condition.split(', ')))
    
    metadata_tmin, metadata_tmax = config['metadata_tmin'], config['metadata_tmax']

    row_events = [k for k in event_id.keys() if k[0:7] == 'stimulus']

    keep_last = ['stimulus', 'response']

    metadata, events, event_id = mne.epochs.make_metadata(
        events=events, event_id=event_id, 
        tmin=metadata_tmin, tmax=metadata_tmax, sfreq=raw.info['sfreq'],
        row_events=row_events,
        keep_last=keep_last)
    
    target_left = [stim for stim in row_events if stim[-4:-1] == 'left']
    target_right = [stim for stim in row_events if stim[-5:-1] == 'right']

    metadata.loc[metadata['last_stimulus'].isin(target_left),
              'stimulus_side'] = 'left'
    metadata.loc[metadata['last_stimulus'].isin(target_right),
              'stimulus_side'] = 'right'

    metadata['response_correct'] = False
    metadata.loc[metadata['stimulus_side'] == metadata['last_response'],
             'response_correct'] = True
    
    id_list = [v for k, v in event_id.items() if k[0:3] != 'stim']

    events = mne.pick_events(events, include=id_list)

    epochs = epoch(config['pick_meg'],config['pick_eeg'],config['pick_eog'], 
                   config['pick_ecg'],config['pick_emg'],config['param_stim'], config['plot_cond'], 
                   config['pick'], event_id, raw, events, tmin=tmin, tmax=tmax, metadata=metadata)

if __name__ == '__main__':
    main()
