# app-epoch

Brainlife App to create epochs based on the events recorded in the Raw object’s STIM channels or event.tsv using MNE-Python Epoch method [mne.Epochs function](https://mne.tools/stable/generated/mne.Epochs.html)

1) Input file is: 
    * `meg/fif` meg data file
    * event.tsv (optional)
    * tmin and tmax (Start and end time of the epochs in seconds, relative to the time-locked event)
    * meg bool
    If True include MEG channels. 
    
    * eeg bool
    If True include EEG channels.
    
    * stim bool
    If True include stimulus channels.
    
    * eog bool
    If True include EOG channels.
    
    * ecg bool
    If True include ECG channels.
    
    * emg bool
    If True include EMG channels.

2) Ouput files are:
    * `epochs/fif`
    * HTML report


## Authors
- Saeed Zahran (saeed.zahran@icm-institute.org)
