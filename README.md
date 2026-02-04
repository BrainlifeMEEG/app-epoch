# app-epoch

Brainlife App to create epochs from raw MEG/EEG data based on events using MNE-Python's [mne.Epochs](https://mne.tools/stable/generated/mne.Epochs.html) function.

## Description

This app extracts epochs (time-locked segments) from raw MEG/EEG data based on event markers recorded in stimulus channels or event files. It supports complex event mapping with metadata creation for analyzing behavioral responses alongside brain data.

## Inputs

- **raw.fif**: Raw MEG/EEG data file in MNE format
- **event.tsv** (optional): Events file. If not provided, events are detected from the stimulus channel specified in configuration

## Outputs

- **meg-epo.fif**: Epoched data in MNE format
- **report.html**: HTML report with epoch statistics and visualizations
- **product.json**: Brainlife.io product metadata including visualization images

## Configuration Parameters

### Required
- **stim_channel** (string): Name of the stimulus channel (e.g., "STI 014")
- **tmin** (float): Start time of epoch in seconds relative to event (e.g., -0.5)
- **tmax** (float): End time of epoch in seconds relative to event (e.g., 1.1)
- **event_id_condition_mapping** (string): Event ID mappings (see format below)

### Optional
- **events** (string): Path to events file. If not provided, events are detected from stim_channel
- **assess_correctness** (boolean): If true, assess response correctness based on stimulus-response mapping (default: false)
- **use_correct** (boolean): If true, keep only correct response epochs (requires assess_correctness=true)
- **metadata_tmin** (float): Start time for metadata creation (often same as tmin)
- **metadata_tmax** (float): End time for metadata creation (often same as tmax)
- **param_eeg**, **param_meg**, **param_eog**, **param_ecg**, **param_emg**, **param_stim** (boolean): Channel types to include

### Event ID Condition Mapping Format

Format: `type/label/category-ID,type/label/category-ID,...`

**Examples:**
- Simple: `stimulus/auditory-1,stimulus/visual-2,response/left-3,response/right-4`
- With targets: `stimulus/D_REA/target_right-13,stimulus/REA_D/target_left-14,response/left-25,response/right-26`

**Components:**
- **type**: Event type (e.g., "stimulus", "response")
- **label**: Descriptive label (can include subcategories like D_REA)
- **category** (for assess_correctness): Target or response category (e.g., "target_left", "target_right")
- **ID**: Numeric event code

## Usage

Configuration file example:
```json
{
    "fif": "meg/raw.fif",
    "stim_channel": "STI 014",
    "tmin": -0.5,
    "tmax": 1.1,
    "metadata_tmin": -0.5,
    "metadata_tmax": 1.1,
    "event_id_condition_mapping": "stimulus/auditory/left-1,stimulus/visual/right-2,response/left-3,response/right-4",
    "assess_correctness": true,
    "use_correct": true
}
```

## Technical Details

### Event Detection and Metadata
- Events are automatically detected from stimulus channels or read from event files
- Metadata is created using MNE's [make_metadata](https://mne.tools/stable/generated/mne.epochs.make_metadata.html) function
- Behavioral responses can be aligned with stimulus information for accuracy analysis

### Response Correctness Assessment
When `assess_correctness` is enabled:
1. Stimulus and response events are mapped to target categories
2. Response correctness is determined by matching response type with stimulus target
3. A `response_correct` column is added to epoch metadata
4. If `use_correct` is true, only correct-response epochs are kept

### Output Report
The HTML report includes:
- Epoch statistics (total count)
- Correct/incorrect response counts (if assess_correctness enabled)
- Epochs visualization showing brain activity across trials
- Channels information

## Authors
- [Kami Salibayeva](https://github.com/KSalibay)
- [Maximilien Chaumon](https://github.com/dnacombo), Paris Brain Institute

## Funding Acknowledgement

brainlife.io is publicly funded and for the sustainability of the project it is helpful to acknowledge the use of the platform. We kindly ask that you acknowledge the funding below in your code and publications.

[![NSF-BCS-1734853](https://img.shields.io/badge/NSF_BCS-1734853-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1734853)
[![NSF-BCS-1636893](https://img.shields.io/badge/NSF_BCS-1636893-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1636893)
[![NSF-ACI-1916518](https://img.shields.io/badge/NSF_ACI-1916518-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1916518)
[![NSF-IIS-1912270](https://img.shields.io/badge/NSF_IIS-1912270-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1912270)
[![NIH-NIBIB-R01EB029272](https://img.shields.io/badge/NIH_NIBIB-R01EB029272-green.svg)](https://grantome.com/grant/NIH/R01-EB029272-01)

## Citations

1. Avesani, P., McPherson, B., Hayashi, S. et al. The open diffusion data derivatives, brain data upcycling via integrated publishing of derivatives and reproducible open cloud services. Sci Data 6, 69 (2019). [https://doi.org/10.1038/s41597-019-0073-y](https://doi.org/10.1038/s41597-019-0073-y)
2. Gramfort, A., Luessi, M., Larson, E., et al. MEG and EEG data analysis with MNE-Python. Front. Neurosci. 7, 267 (2013). [https://doi.org/10.3389/fnins.2013.00267](https://doi.org/10.3389/fnins.2013.00267)
