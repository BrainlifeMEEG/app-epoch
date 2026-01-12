"""
Epoch extraction app for Brainlife.io

This app creates epochs from raw MEG/EEG data based on events.

Inputs:
    - raw.fif: Raw MEG/EEG data file
    - event.tsv: Optional events file (if not provided, events are detected from stim channel)

Outputs:
    - meg-epo.fif: Epoched data
    - report.html: HTML report with epoch information and visualizations
    - product.json: Brainlife.io product metadata with visualizations
"""

import mne
import os
import os.path as op
import matplotlib.pyplot as plt
import numpy as np

# Setup matplotlib for headless execution
from brainlife_utils import setup_matplotlib_backend, load_config, ensure_output_dirs, create_product_json, add_info_to_product, add_image_to_product

setup_matplotlib_backend()

# Load config
config = load_config()

# Ensure output directories exist
ensure_output_dirs('out_dir', 'out_figs', 'out_report')

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
 
report.add_epochs(epochs=epochs, title='Epochs from "epochs"')

correct_response_count = metadata['response_correct'].sum() if config.get('assess_correctness') else 0
incorrect_response_count = len(metadata) - correct_response_count if config.get('assess_correctness') else 0

if config.get('assess_correctness'):
    report.add_html(title='Counts of correct responses', html='<div>'+'Correct responses: '+str(correct_response_count)+
           '<br>'+'Incorrect responses: '+str(incorrect_response_count)+'</div>')

# Create epochs plot visualization
fig = epochs.plot_image(combine='gfp', show=False)
epochs_plot_path = os.path.join('out_figs', 'epochs_plot.png')
fig[0].savefig(epochs_plot_path)
plt.close(fig[0])

# Add image to report
report.add_image(epochs_plot_path, title='Epochs Plot')

# Save report
report.save(os.path.join('out_report', 'report.html'), overwrite=True)

# Save file
epochs.save(os.path.join('out_dir', 'meg-epo.fif'), overwrite=True)

# Create product.json
product_items = []
add_info_to_product(product_items, f"Number of epochs: {len(epochs)}")
add_info_to_product(product_items, f"Epoch time window: {tmin} to {tmax} seconds")
if config.get('assess_correctness'):
    add_info_to_product(product_items, f"Correct responses: {correct_response_count}")
    add_info_to_product(product_items, f"Incorrect responses: {incorrect_response_count}")
add_image_to_product(product_items, epochs_plot_path, 'epochs_plot.png')

create_product_json(product_items)
