import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import nibabel as nib
from nltools.file_reader import onsets_to_dm
from nltools.stats import regress, zscore
from nltools.data import Brain_Data, Design_Matrix
from nltools.stats import find_spikes 
from nltools.mask import expand_mask, roi_to_brain
from nltools.utils import concatenate
import argparse
from itertools import combinations
import time, random

time.sleep(random.randint(5, 20))

bids_dir = '/srv/lab/fmri/mft/fhopp_diss/bids'
deriv_dir = '/srv/lab/fmri/mft/fhopp_diss/bids/derivatives/fmriprep'
output_dir = '/srv/lab/fmri/mft/fhopp_diss/analysis/vignettes/mvpa/betas/test/'

parser = argparse.ArgumentParser()
parser.add_argument('-subject', type=str, required=True, dest='subject')

args = parser.parse_args()
subject = 'sub-' + args.subject

bids_dir = '/srv/lab/fmri/mft/fhopp_diss/bids'
deriv_dir = '/srv/lab/fmri/mft/fhopp_diss/bids/derivatives/fmriprep'
output_dir = '/srv/lab/fmri/mft/fhopp_diss/analysis/vignettes/mvpa/betas/new_runwise_ratings_zscored/'

tr = 0.72
fwhm = 6
spike_cutoff = 3

nifti_paths = sorted([x for x in glob.glob(os.path.join(deriv_dir, '*/func/*preproc*gz')) if 'vignette' in x and subject in x] )
onset_paths = sorted([x for x in glob.glob(os.path.join(bids_dir, '*/func/*events*tsv')) if 'vignette' in x and subject in x] )
cov_paths = sorted([x for x in glob.glob(os.path.join(deriv_dir, '*/func/*confounds*tsv')) if 'vignette' in x and subject in x] )
beh_paths = sorted([x for x in glob.glob(os.path.join(bids_dir, '*/beh/*tsv')) if 'vignette' in x and subject in x] )

conds = {'carem':'Care Emotional',
             'carep':'Care Physical',
             'fair':'Fairness',
             'lib':'Liberty',
             'loy':'Loyalty',
             'auth':'Authority',
             'pur':'Purity',
             'socn':'Social'}

def load_bids_events(onset_path, beh_path):
    '''Create a design_matrix instance from BIDS event file'''
    
    tr = 0.72
    n_tr = 668
    
    onsets = pd.read_csv(onset_path, sep='\t',usecols=['onset','duration','trial_type', 'stim_file'])
    onsets['onset'] = onsets['onset'] - 5.76
    onsets['duration'] = 7.92
    
    ratings = pd.read_csv(beh_path, sep='\t',usecols=['moral_decision'])
    onsets = onsets.join(ratings)
    onsets = onsets.dropna(subset=['moral_decision'])
    ratings = onsets.copy(deep=True)
    ratings['trial_type'] = ratings['moral_decision'].astype(int).astype(str)
    ratings = ratings[['onset','duration','trial_type']]
    ratings.columns = ['Onset', 'Duration', 'Stim']
    
    onsets = onsets[['onset','duration','trial_type']]
    onsets.columns = ['Onset', 'Duration', 'Stim']
    
    return onsets_to_dm(onsets, sampling_freq=1./tr, run_length=n_tr), onsets_to_dm(ratings, sampling_freq=1./tr, run_length=n_tr)

def make_motion_covariates(mc):
    z_mc = zscore(mc)
    all_mc = pd.concat([z_mc, z_mc**2, z_mc.diff(), z_mc.diff()**2], axis=1)
    all_mc.fillna(value=0, inplace=True)
    return Design_Matrix(all_mc, sampling_freq=1/tr)

# brain_data = {}
# Construct DMs, Convolve with HRF, Add DCT Basis, and Poly drifts
all_runs = Design_Matrix(sampling_freq = 1./tr)

for nifti_path, onset_path, cov_path, beh_path in zip(nifti_paths, onset_paths, cov_paths, beh_paths):
    
     # 1) Load in onsets for this run
    dm, md = load_bids_events(onset_path, beh_path)
    md['moral_rating'] = md.idxmax(axis=1)
    dm['moral_rating'] = md['moral_rating'].astype(int)
    for c in dm.columns:
        if c != 'moral_rating':
            dm[c] = dm[c] * dm['moral_rating']
    del dm['moral_rating']
    
    run = nifti_path.split('_')[3]
    print("Loading Run: ", run)
    data = Brain_Data(nifti_path)[11:-11].smooth(fwhm=fwhm)
   
    # 3) Load in covariates for this run
    covariates = pd.read_csv(cov_path, sep='\t')[11:-11].reset_index(drop=True)
    mc_cov = make_motion_covariates(covariates[['trans_x','trans_y','trans_z','rot_x', 'rot_y', 'rot_z']])
    spikes = data.find_spikes(global_spike_cutoff=spike_cutoff, diff_spike_cutoff=spike_cutoff)
    dm_cov = dm.convolve().add_dct_basis(duration=90).add_poly(order=1, include_lower=True)
    dm_cov = dm_cov.append(mc_cov, axis=1).append(Design_Matrix(spikes.iloc[:, 1:], sampling_freq=1/tr), axis=1)
    data.X = dm_cov
    stats = data.regress()

    for cond, name in conds.items():
        for i, col in enumerate(data.X.columns):
            if col.startswith(cond):
                stats['beta'][i].standardize(axis=0, method='zscore').write(output_dir + f"{subject}_{name}_{run}.nii.gz")