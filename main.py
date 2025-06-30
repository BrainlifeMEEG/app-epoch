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
import base64

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
data_file = config['fif']

# Read the event time
tmin = config['tmin']
tmax = config['tmax']

raw = mne.io.read_raw_fif(data_file, verbose=False)

if 'events' in config and config['events'] is not None:
   events_file = config['events']
   if op.exists(events_file):
       events = mne.read_events(events_file)
   else:
       events = mne.find_events(raw, stim_channel=config['stim_channel'])
else:
   events = mne.find_events(raw, stim_channel=config['stim_channel'])

event_id_condition= config['event_id_condition_mapping']

event_id = dict((x.strip(), int(y.strip()))
                 for x, y in (element.split('-')
                              for element in event_id_condition.split(',')))


metadata_tmin, metadata_tmax = config['metadata_tmin'], config['metadata_tmax']

row_events = [k for k in event_id.keys() if 'stimulus' in k]

keep_last = ['stimulus', 'response']

response_count = len(set([k for k in event_id.keys() if 'response' in k]))

response_types = [k.split('/')[1] for k in event_id.keys() if 'response' in k]

metadata, events, event_id = mne.epochs.make_metadata(
    events=events, event_id=event_id, 
    tmin=metadata_tmin, tmax=metadata_tmax, sfreq=raw.info['sfreq'],
    row_events=row_events,
    keep_last=keep_last)


targets = {}

for response_type in response_types:
    for stim in row_events:
        if response_type in stim:
            target = stim.split('/')[-1].split('-')[0].replace('target_', '')
            targets[response_type] = target
            break

# Now we can assign the stimulus_side based on the last_stimulus and the response type
metadata['stimulus_side'] = 'unknown'  # Initialize with a default value
for response_type, target in targets.items():
    metadata.loc[metadata['last_stimulus'].str.contains(target), 'stimulus_side'] = response_type
    
# Now if we want to assess correctness, we can do so by checking if the last_response matches the stimulus_side
if config['assess_correctness']:
    metadata['response_correct'] = False
    metadata.loc[metadata['stimulus_side'] == metadata['last_response'],
                 'response_correct'] = True


id_list = [v for k, v in event_id.items() if k[0:3] != 'stim']

events = mne.pick_events(events, include=id_list)

report = mne.Report(title='Report')

epochs = mne.Epochs(raw=raw, events=events, event_id=event_id, metadata=metadata, tmin=tmin, tmax=tmax, preload=True)

if config['use_correct']:
    epochs = epochs['response_correct']

if len(epochs) == 0:
    raise ValueError("No epochs were created. Please check your event_id and tmin/tmax parameters.")

report.add_epochs(epochs=epochs, title='Epochs from "epochs"')

correct_response_count = metadata['response_correct'].sum()
incorrect_response_count = len(metadata) - correct_response_count

report.add_html(title='Counts of correct responses',html='<dev>'+'Correct responses: '+str(correct_response_count)+
       '<br>'+'Incorrect responses: '+str(incorrect_response_count)+'</dev>')
 
 # == SAVE REPORT ==
report.save(os.path.join('out_dir_report','report.html'), overwrite=True)

 # == SAVE FILE ==
epochs.save(os.path.join('out_dir', 'meg-epo.fif'), overwrite=True)

# Create and save epochs plot without displaying it
fig = epochs.plot_image(combine='gfp',show=False)
fig[0].savefig(os.path.join('out_figs', 'epochs_plot.png'))
plt.close(fig[0])  # Close the figure to free memory

# Read PNG and convert to base64 in one step
png_path = os.path.join('out_figs', 'epochs_plot.png')
data_uri = base64.b64encode(open(png_path, 'rb').read()).decode('utf-8')

dict_json_product = {'brainlife': []}
dict_json_product['brainlife'].append({'type': 'image/png', 'name': 'Epochs', 'base64': data_uri})

with open('product.json', 'w') as outfile:
    json.dump(dict_json_product, outfile)
