# First-level GLM via Nipype & SPM 

from os.path import join as opj
import json
from nipype.interfaces.spm import Level1Design, EstimateModel, EstimateContrast
from nipype.algorithms.modelgen import SpecifySPMModel
from nipype.interfaces.utility import Function, IdentityInterface
from nipype.interfaces.io import SelectFiles, DataSink
from nipype import Workflow, Node, MapNode
from nipype.interfaces.fsl import ExtractROI
from nipype.algorithms.misc import Gunzip
from nipype.interfaces.spm import Smooth
import argparse

# Get current user
import getpass
import os

user = getpass.getuser()
print('Running code as: ', user)

data_dir = '/home/{}/spm/bids/'.format(user) # BIDS main
exp_dir = '/home/{}/spm/analysis/vignettes/glm/spm/'.format(user)
output_dir = os.path.join(exp_dir + "out") # Output for analyses
experiment_dir = '/home/{}/spm/bids/'.format(user) # BIDS main
output_dir = os.path.join(exp_dir + "out") # Output for analyses
working_dir = '/home/{}/spm/analysis/vignettes/glm/spm/'.format(user)

# list of subject identifiers
parser = argparse.ArgumentParser()
parser.add_argument('-subject', type=str, required=True, dest='subject')

args = parser.parse_args()
subject = 'sub-' + args.subject
subject_list = [subject]

TR = 0.72
fwhm = [6,6,6]

# Build Workflow

# 1) Unzip functional image and brain mask
gunzip = MapNode(Gunzip(), name="gunzip", iterfield=['in_file'])
mask_gunzip = Node(Gunzip(), name="mask_gunzip", iterfield=['in_file'])

# 2) Drop dummy scans
extract = MapNode(
    ExtractROI(t_min=11, t_size=668, output_type="NIFTI"),
    iterfield=["in_file"],
    name="Remove_Dummies")

# 3) Smooth 
smooth = Node(Smooth(fwhm=fwhm),
              name="smooth")

# 4) SpecifyModel - Generates SPM-specific Model
modelspec = Node(SpecifySPMModel(concatenate_runs=False,
                                 input_units='secs',
                                 output_units='secs',
                                 time_repetition=TR,
                                 high_pass_filter_cutoff=90),
                 name="modelspec")

# 5) Level1Design - Generates an SPM design matrix
level1design = Node(Level1Design(bases={'hrf': {'derivs': [1, 0]}},
                                 timing_units='secs',
                                 interscan_interval=TR,
                                 model_serial_correlations='AR(1)'),
                    name="level1design")

# 6) EstimateModel - estimate the parameters of the model
level1estimate = Node(EstimateModel(estimation_method={'Classical': 1}),
                      name="level1estimate")

# 7) EstimateContrast - estimates contrasts
level1conest = Node(EstimateContrast(), name="level1conest")
# 8) Condition names & Contrasts 
condition_names = ['carep','carem','fair','lib',
                  'loy','auth','pur','socn']

cont01 = ['Average', 'T', condition_names, [1/8., 1/8., 1/8., 1/8., 1/8., 1/8.,1/8., 1/8.]]
cont02 = ['Physical Harm', 'T', condition_names, [1, 0, 0, 0, 0, 0, 0, 0]]
cont03 = ['Emotional Harm', 'T', condition_names, [0, 1, 0, 0, 0, 0, 0, 0]]
cont04 = ['Cheating','T', condition_names, [0, 0, 1, 0, 0, 0, 0, 0]]
cont05 = ['Oppression','T', condition_names, [0, 0, 0, 1, 0, 0, 0, 0]]
cont06 = ['Betrayal','T', condition_names, [0, 0, 0, 0, 1, 0, 0, 0]]
cont07 = ['Subversion','T', condition_names, [0, 0, 0, 0, 0, 1, 0, 0]]
cont08 = ['Degradation','T', condition_names, [0, 0, 0, 0, 0, 0, 1, 0]]
cont09 = ['Social','T', condition_names, [0, 0, 0, 0, 0, 0, 0, 1]]

cont10 = ['Physical Harm > others','T', condition_names, [1, -1/7., -1/7., -1/7., -1/7., -1/7., -1/7., -1/7.]]
cont11 = ['Emotional Harm > others','T', condition_names, [-1/7, 1, -1/7., -1/7., -1/7., -1/7., -1/7., -1/7.]]
cont12 = ['Cheating > others','T', condition_names, [-1/7, -1/7., 1, -1/7., -1/7., -1/7., -1/7., -1/7.]]
cont13 = ['Oppression > others','T', condition_names, [-1/7, -1/7., -1/7., 1, -1/7., -1/7., -1/7., -1/7.]]
cont14 = ['Betrayal > others','T', condition_names, [-1/7, -1/7., -1/7., -1/7., 1, -1/7., -1/7., -1/7.]]
cont15 = ['Subversion > others','T', condition_names, [-1/7, -1/7., -1/7., -1/7., -1/7., 1, -1/7., -1/7.]]
cont16 = ['Degradation > others','T', condition_names, [-1/7, -1/7., -1/7., -1/7., -1/7., -1/7., 1/7., -1/7.]]
cont17 = ['Social > others','T', condition_names, [-1/7, -1/7., -1/7., -1/7., -1/7., -1/7., -1/7., 1]]

cont18 = ['Physical Harm > Social','T', condition_names, [1, 0, 0, 0, 0, 0, 0, -1]]
cont19 = ['Emotional Harm > Social','T', condition_names, [0, 1, 0, 0, 0, 0, 0, -1]]
cont20 = ['Cheating > Social','T', condition_names, [0, 0, 1, 0, 0, 0, 0, -1]]
cont21 = ['Oppression > Social','T', condition_names, [0, 0, 0, 1, 0, 0, 0, -1]]
cont22 = ['Betrayal > Social','T', condition_names, [0, 0, 0, 0, 1, 0, 0, -1]]
cont23 = ['Subversion > Social','T', condition_names, [0, 0, 0, 0, 0, 1, 0, -1]]
cont24 = ['Degradation > Social','T', condition_names, [0, 0, 0, 0, 0, 0, 1, -1]]

cont25 = ['Binding > Individualizing','T', condition_names, [-1/3., -1/3., -1/3., 0, 1/3., 1/3., 1/3., 0]]
cont26 = ['Moral > Social','T', condition_names, [1/7., 1/7., 1/7., 1/7., 1/7., 1/7., 1/7., -1]]

contrast_list = [cont01, cont02, cont03, cont04, cont05, cont06, cont07, cont08, cont09,
                cont10, cont11, cont12, cont13, cont14, cont15, cont16, cont17,
                cont18, cont19, cont20, cont21, cont22, cont23, cont24, 
                cont25,cont26]

# 9) Function to get Subject specific condition information
def get_subject_info(subject_id):
    from os.path import join as opj
    import pandas as pd
    onset_path = '/home/fhopp/spm/bids/%s'%subject_id
    nr_path = '/home/fhopp/spm/bids/derivatives/fmriprep/%s'%subject_id
    
    subjectinfo = []
    
    if subject_id == "sub-35":
        runs = ['01', '02']
    else:
        runs = ['01', '02', '03']
        
    for run in runs:
        onset_file = opj(onset_path, 'func/%s_task-vignette_run-%s_events.tsv'%(subject_id, run))
        
        ev = pd.read_csv(onset_file, sep="\t", usecols=['onset','duration','trial_type'])
        ev['onset'] = ev['onset'] - 5.76
        ev['duration'] = 7.92
        
        regressor_file = opj(nr_path, 'func/%s_task-vignette_run-%s_desc-confounds_timeseries.tsv'%(subject_id, run[1]))
        nuisance_reg = ['dvars', 'framewise_displacement'] + \
        ['a_comp_cor_%02d' % i for i in range(6)] + ['cosine%02d' % i for i in range(4)]
        
        nr = pd.read_csv(regressor_file, sep="\t", usecols=nuisance_reg).iloc[11:-11]
        
        from nipype.interfaces.base import Bunch
        run_info = Bunch(onsets=[], durations=[])

        run_info.set(conditions=[g[0] for g in ev.groupby("trial_type")])
        run_info.set(regressor_names=nr.columns.tolist())
        run_info.set(regressors=nr.T.values.tolist())

        for group in ev.groupby("trial_type"):
            run_info.onsets.append(group[1].onset.tolist())
            run_info.durations.append(group[1].duration.tolist())
            
        subjectinfo.insert(int(run)-1,
                           run_info)
       
    return subjectinfo

getsubjectinfo = Node(Function(input_names=['subject_id'],
                               output_names=['subject_info'],
                               function=get_subject_info),
                      name='getsubjectinfo')

# Infosource - a function free node to iterate over the list of subject names
infosource = Node(IdentityInterface(fields=['subject_id','contrasts'],
                                    contrasts=contrast_list),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]

# SelectFiles - to grab the data (alternativ to DataGrabber)
templates = {'func': '/home/fhopp/spm/bids/derivatives/fmriprep/{subject_id}/func/{subject_id}_task-vignette_run-*_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz',
            'mask': '/home/fhopp/spm/bids/derivatives/fmriprep/{subject_id}/anat/{subject_id}_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz'}
selectfiles = Node(SelectFiles(templates,
                               base_directory=experiment_dir,
                               sort_filelist=True),
                   name="selectfiles")

# Datasink - creates output folder for important outputs
datasink = Node(DataSink(base_directory=experiment_dir,
                         container=output_dir),
                name="datasink")

# Use the following DataSink output substitutions
substitutions = [('_subject_id_', ''),]
datasink.inputs.substitutions = substitutions
subjFolders = [('sub-%s' % sub)
               for sub in subject_list]
substitutions.extend(subjFolders)

# Initiation of the 1st-level analysis workflow
l1analysis = Workflow(name='l1analysis')
l1analysis.base_dir = opj(experiment_dir, working_dir)

# Connect up the 1st-level analysis components
l1analysis.connect([(infosource, selectfiles, [('subject_id', 'subject_id')]),
                    (infosource, getsubjectinfo, [('subject_id',
                                                   'subject_id')]),
                    (getsubjectinfo, modelspec, [('subject_info',
                                                  'subject_info')]),
                    (infosource, level1conest, [('contrasts', 'contrasts')]),
                    (selectfiles, gunzip, [('func', 'in_file')]),
                    (selectfiles, mask_gunzip, [('mask', 'in_file')]),
                    (gunzip, extract, [('out_file', 'in_file')]),
                    (extract, smooth, [('roi_file', 'in_files')]),
                    (smooth, modelspec, [('smoothed_files', 'functional_runs')]),
                    (modelspec, level1design, [('session_info',
                                                'session_info')]),
                    (mask_gunzip, level1design, [('out_file',
                                                'mask_image')]),
                    (level1design, level1estimate, [('spm_mat_file',
                                                     'spm_mat_file')]),
                    (level1estimate, level1conest, [('spm_mat_file',
                                                     'spm_mat_file'),
                                                    ('beta_images',
                                                     'beta_images'),
                                                    ('residual_image',
                                                     'residual_image')]),
                    (level1conest, datasink, [('spm_mat_file', '1stLevel.@spm_mat'),
                                              ('spmT_images', '1stLevel.@T'),
                                              ('con_images', '1stLevel.@con'),
                                              ('spmF_images', '1stLevel.@F'),
                                              ('ess_images', '1stLevel.@ess'),
                                              ]),
                    ])

l1analysis.config["execution"]["crashfile_format"] = "txt"
l1analysis.run('MultiProc', plugin_args={'n_procs': 7})