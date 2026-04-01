"""
Epoch extraction app for Brainlife.io

This app creates epochs from raw MEG/EEG data based on events using MNE-Python's 
mne.Epochs function. It supports complex event mapping with metadata creation for 
analyzing behavioral responses alongside brain data.

Inputs:
    - raw.fif: Raw MEG/EEG data file in MNE format
    - event.tsv (optional): Events file. If not provided, events are detected from stim channel

Outputs:
    - out_dir/meg-epo.fif: Epoched data in MNE format
    - out_figs/epochs_plot.png: Visualization of epoched data
    - out_report/report.html: HTML report with epoch statistics and visualizations
    - product.json: Brainlife.io product metadata including visualization images
"""

# Copyright (c) 2026 brainlife.io
#
# This app creates epochs from raw MEG/EEG data.
#
# Authors:
# - Kami Salibayeva (https://github.com/KSalibay)
# - Maximilien Chaumon (https://github.com/dnacombo)

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'brainlife_utils'))

# Standard imports
import mne
import os.path as op
import matplotlib.pyplot as plt
import numpy as np
import base64

# Import shared utilities
from brainlife_utils import (
    load_config,
    setup_matplotlib_backend,
    ensure_output_dirs,
    create_product_json,
    add_info_to_product,
    add_image_to_product
)

# Set up matplotlib for headless execution
setup_matplotlib_backend()

# Ensure output directories exist
ensure_output_dirs('out_dir', 'out_figs', 'out_report')

# Load configuration
config = load_config()

# == LOAD DATA ==
# Read raw data file
raw = mne.io.read_raw_fif(config['raw'], verbose=False)

# Get epoch time window
tmin = config['tmin']
tmax = config['tmax']
# parse comma separated picks into list
picks = config['picks']
if picks:
    config['picks'] = [pick.strip() for pick in picks.split(',')]

# == LOAD EVENTS ==
# Load events from file or detect from raw data
# Load events from file if provided, otherwise detect from stim channel
events_file = config.get('events')
if events_file and op.exists(events_file):
    events = mne.read_events(events_file)
else:
    stim_channel = config.get('stim_channel')
    if not stim_channel:
        # use annotations in raw data if no stim channel specified
        events, _ = mne.events_from_annotations(raw)
    else:
        events = mne.find_events(raw, stim_channel=stim_channel)

# == PARSE EVENT ID MAPPING ==
# Parse event_id_condition_mapping into event_id dictionary
event_id_condition = config['event_id_condition_mapping']
event_id = dict((x.strip(), int(y.strip()))
                for x, y in (element.split('-')
                             for element in event_id_condition.split(',')))

# Get event types from configuration
event1 = config['event1kw']  # e.g., 'stimulus'
event2 = config['event2kw']  # e.g., 'response'

# == CREATE METADATA ==
metadata_tmin = config['metadata_tmin']
metadata_tmax = config['metadata_tmax']

# Identify events for metadata creation
row_events = [k for k in event_id.keys() if event1 in k]
keep_last = [event1, event2]

# Extract event type labels
event2_types = [k.split('/')[1] for k in event_id.keys() if event2 in k]

# Create metadata linking events together
metadata, events, event_id = mne.epochs.make_metadata(
    events=events, event_id=event_id,
    tmin=metadata_tmin, tmax=metadata_tmax, sfreq=raw.info['sfreq'],
    row_events=row_events,
    keep_last=keep_last)

# == ASSESS RESPONSE CORRECTNESS ==
if config.get('assess_correctness', False):
    # Build mapping of event2 types to event1 targets
    targets = {}
    for event2_type in event2_types:
        for stim in row_events:
            if event2_type in stim:
                target = stim.split('/')[-1].split('-')[0]
                targets[event2_type] = target
                break
    
    # Assign event1 type based on target information
    metadata[f'{event1}_type'] = 'unknown'
    for event2_type, target in targets.items():
        metadata.loc[metadata[f'last_{event1}'].str.contains(target), f'{event1}_type'] = event2_type
    
    # Assess correctness: does last_event2 match the inferred event1_type?
    metadata[f'{event2}_correct'] = False
    metadata.loc[metadata[f'{event1}_type'] == metadata[f'last_{event2}'],
                 f'{event2}_correct'] = True
else:
    # Initialize correctness column as all True if not assessing
    metadata[f'{event2}_correct'] = True


# == CREATE EPOCHS ==
epochs = mne.Epochs(raw=raw, events=events, event_id=event_id, picks = picks,
                    metadata=metadata,
                    tmin=tmin, tmax=tmax, preload=True)

# Filter to correct responses if requested
if config.get('use_correct', False) and config.get('assess_correctness', False):
    epochs = epochs[f'{event2}_correct']

if len(epochs) == 0:
    raise ValueError("No epochs were created. Please check your event_id and tmin/tmax parameters.")

# == CREATE REPORT ==
report = mne.Report(title='Epoch Extraction Report')

# Add epochs visualization
report.add_epochs(epochs=epochs, title='Epoched Data')

# Add statistics if assessing correctness
if config.get('assess_correctness', False):
    correct_count = metadata[f'{event2}_correct'].sum()
    incorrect_count = len(metadata) - correct_count
    report.add_html(
        title=f'Response Correctness',
        html=f'<div>'
             f'Correct {event2}s: {correct_count}<br>'
             f'Incorrect {event2}s: {incorrect_count}'
             f'</div>'
    )

# == CREATE VISUALIZATIONS ==
# Create epochs plot visualization
fig = epochs.plot_image(combine='gfp', show=False)
epochs_plot_path = os.path.join('out_figs', 'epochs_plot.png')
fig[0].savefig(epochs_plot_path)
plt.close(fig[0])

# Save report
report.save(os.path.join('out_report', 'report.html'), overwrite=True)

# == SAVE EPOCHED DATA ==
epochs.save(os.path.join('out_dir', 'meg-epo.fif'), overwrite=True)

# == CREATE PRODUCT JSON ==
product_items = []
add_info_to_product(product_items, "Epochs created successfully from raw data.", msg_type='success')
add_info_to_product(product_items, f"Number of epochs: {len(epochs)}")
add_info_to_product(product_items, f"Epoch time window: {tmin} to {tmax} seconds")

if config.get('assess_correctness', False):
    correct_count = metadata[f'{event2}_correct'].sum()
    incorrect_count = len(metadata) - correct_count
    add_info_to_product(product_items, f"Correct {event2}s: {correct_count}")
    add_info_to_product(product_items, f"Incorrect {event2}s: {incorrect_count}")

with open(epochs_plot_path, 'rb') as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    add_image_to_product(product_items, 'Epochs plot', base64_data=img_base64)

create_product_json(product_items)
