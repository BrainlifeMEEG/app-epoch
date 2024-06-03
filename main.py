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


# Current path
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

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
#mask = 4096 + 256  # mask for excluding high order bits

if config.get('events') is not None:
   events_file = config.pop('events')
   if op.exists(events_file):
       events = mne.read_events(events_file)
   else:
       events = mne.find_events(raw, stim_channel=config['stim_channel'])
else:
   events = mne.find_events(raw, stim_channel=config['stim_channel'])

event_id_condition= config['event_id_condition_mapping']

#Convert String to Dictionary using strip() and split() methods
event_id = dict((x.strip(), int(y.strip()))
                 for x, y in (element.split('-')
                              for element in event_id_condition.split(',')))


metadata_tmin, metadata_tmax = config['metadata_tmin'], config['metadata_tmax']

row_events = [k for k in event_id.keys() if 'stimulus' in k]

keep_last = ['stimulus', 'response']

#Let's count the number of possible responses (i.e. the number of unique values in the event_id dictionary that have 'response' in the key)
response_count = len(set([k for k in event_id.keys() if 'response' in k]))

metadata, events, event_id = mne.epochs.make_metadata(
    events=events, event_id=event_id, 
    tmin=metadata_tmin, tmax=metadata_tmax, sfreq=raw.info['sfreq'],
    row_events=row_events,
    keep_last=keep_last)

#Now we need to reformat the code below to allow more than 2 responses

#Let's extract what types of responses there are
#That is determined by the text following the '/' in the event_id dictionary items with 'response' in the key

response_types = [k.split('/')[1] for k in event_id.keys() if 'response' in k]

#For now, let's assume that there are only two types of responses

target_1 = [stim[9:] for stim in row_events if stim[-4:] == response_types[0]]
target_2 = [stim[9:] for stim in row_events if stim[-5:] == response_types[1]]

metadata.loc[metadata['last_stimulus'].isin(target_1),
          'stimulus_side'] = response_types[0]
metadata.loc[metadata['last_stimulus'].isin(target_2),
          'stimulus_side'] = response_types[1]

metadata['response_correct'] = False
metadata.loc[metadata['stimulus_side'] == metadata['last_response'],
         'response_correct'] = True

id_list = [v for k, v in event_id.items() if k[0:3] != 'stim']

events = mne.pick_events(events, include=id_list)

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
incorrect_response_count = len(metadata) - correct_response_count

report.add_html(title='Counts of correct responses',html='<dev>'+'Correct responses: '+str(correct_response_count)+
       '<br>'+'Incorrect responses: '+str(incorrect_response_count)+'</dev>')
 
 # == SAVE REPORT ==
report.save(os.path.join('out_dir_report','report.html'), overwrite=True)

 # == SAVE FILE ==
epochs.save(os.path.join('out_dir', 'meg-epo.fif'), overwrite=True)
