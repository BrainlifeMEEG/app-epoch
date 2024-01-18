# app-epoch

Brainlife App to create epochs based on the events recorded in the Raw object’s STIM channels or event.tsv using MNE-Python Epoch method [mne.Epochs function](https://mne.tools/stable/generated/mne.Epochs.html).

If you want to epoch according to certain event codes, you need to create a mapping between event IDs (1,2,3..., as coded in 'STI 014' or other stimulus aggregate channel) and desired labels (e.g. 'auditory', 'visual', or any other stimulus names that make sense in your design). The mapping should be formatted with dashes (-) between a desired label and the ID code and commas (,) between list entries like so: auditory-1,visual-2, etc. 

If you toggle "assess_correctness", then you need to provide additional information about your events and the correct response (for stimulus), as well as responses and their types. 

The information should be formatted as follows: type_of_event/desired_label/(correct_response)-event_ID 

Example: stimulus/auditory/left-1,stimulus/visual/right-2,response/left-3,response/right-4

1) Input file is: 
    * `meg/fif` meg data file
    * `event.tsv` (optional)
    * `tmin` and `tmax` (Start and end time of the epochs in seconds, relative to the time-locked event)


2) Ouput files are:
    * `epochs/fif`
    * `HTML report`


## Authors
- [Kami Salibayeva] (ksalibay@iu.edu)

### Contributors
- [Maximilien Chaumon] (maximilien.chaumon@icm-institute.org)
- [Kami Salibayeva] (ksalibay@iu.edu)

### Funding Acknowledgement
brainlife.io is publicly funded and for the sustainability of the project it is helpful to Acknowledge the use of the platform. We kindly ask that you acknowledge the funding below in your code and publications. Copy and past the following lines into your repository when using this code.

[![NSF-BCS-1734853](https://img.shields.io/badge/NSF_BCS-1734853-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1734853)
[![NSF-BCS-1636893](https://img.shields.io/badge/NSF_BCS-1636893-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1636893)
[![NSF-ACI-1916518](https://img.shields.io/badge/NSF_ACI-1916518-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1916518)
[![NSF-IIS-1912270](https://img.shields.io/badge/NSF_IIS-1912270-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1912270)
[![NIH-NIBIB-R01EB029272](https://img.shields.io/badge/NIH_NIBIB-R01EB029272-green.svg)](https://grantome.com/grant/NIH/R01-EB029272-01)

### Citations
1. Avesani, P., McPherson, B., Hayashi, S. et al. The open diffusion data derivatives, brain data upcycling via integrated publishing of derivatives and reproducible open cloud services. Sci Data 6, 69 (2019). [https://doi.org/10.1038/s41597-019-0073-y](https://doi.org/10.1038/s41597-019-0073-y)
2. Taulu S. and Kajola M. Presentation of electromagnetic multichannel data: The signal space separation method. Journal of Applied Physics, 97 (2005). [https://doi.org/10.1063/1.1935742](https://doi.org/10.1063/1.1935742)
3. Taulu S. and Simola J. Spatiotemporal signal space separation method for rejecting nearby interference in MEG measurements. Physics in Medicine and Biology, 51 (2006). [https://doi.org/10.1088/0031-9155/51/7/008](https://doi.org/10.1088/0031-9155/51/7/008)

