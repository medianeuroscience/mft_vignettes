# Second-level GLM via Nipype & SPM12 

from nipype import Node, Workflow
from nipype import SelectFiles
from nipype.interfaces.spm import OneSampleTTestDesign
from nipype.interfaces.spm import EstimateModel, EstimateContrast
from nipype.interfaces.spm import Threshold
from nipype.interfaces.io import DataSink

# Get current user
import getpass
import os

user = getpass.getuser()
print('Running code as: ', user)

exp_dir = '/home/{}/spm/analysis/vignettes/glm/spm'.format(user)
workflow_dir = '/home/{}/spm/analysis/vignettes/glm/spm/nipype_workflows'.format(user)

analysis2nd = Workflow(name='2nd_lv_smoothed_avg_cond', base_dir=workflow_dir)

onesamplettestdes = Node(OneSampleTTestDesign(), name="onesampttestdes")

level2estimate = Node(EstimateModel(estimation_method={'Classical': 1}),
                      name="level2estimate")

level2conestimate = Node(EstimateContrast(group_contrast=True),
                         name="level2conestimate")
cont1 = ['Group', 'T', ['mean'], [1]]
level2conestimate.inputs.contrasts = [cont1]

analysis2nd.connect([(onesamplettestdes, level2estimate, [('spm_mat_file',
                                                           'spm_mat_file')]),
                     (level2estimate, level2conestimate, [('spm_mat_file',
                                                           'spm_mat_file'),
                                                          ('beta_images',
                                                           'beta_images'),
                                                          ('residual_image',
                                                           'residual_image')])
                    ])

level2thresh = Node(Threshold(contrast_index=1,
                              use_topo_fdr=True,
                              use_fwe_correction=False,
                              extent_threshold=0,
                              height_threshold=0.001,
                              height_threshold_type='p-value',
                              extent_fdr_p_threshold=0.01),
                    name="level2thresh")

analysis2nd.connect([(level2conestimate, level2thresh, [('spm_mat_file',
                                                         'spm_mat_file'),
                                                        ('spmT_images',
                                                         'stat_image'),
                                                       ])
                    ])

# String template with {}-based strings
templates = {'cons': '/home/fhopp/spm/analysis/vignettes/glm/spm/results/1st_lv_smoothed_avgcond/sub-*/con_{cont_id}.nii'}


# Create SelectFiles node
sf = Node(SelectFiles(templates, sort_filelist=True),
          name='selectfiles')

# list of contrast identifiers (see first_lv.py for definitions)
contrast_id_list = [
                    '0009', '0010', '0011', '0012', '0013',
                    '0014', '0015', '0016', '0017']
sf.iterables = [('cont_id', contrast_id_list)]
analysis2nd.connect([(sf, onesamplettestdes, [('cons', 'in_files')])])

# Initiate the datasink node
output_folder = 'results'
datasink = Node(DataSink(base_directory=exp_dir,
                         container=output_folder),
                name="datasink")

## Use the following substitutions for the DataSink output
substitutions = [('_cont_id_', 'con_')]
datasink.inputs.substitutions = substitutions

analysis2nd.connect([(level2conestimate, datasink, [('spm_mat_file',
                                                     '2nd_lv_smoothed_avgcond.@spm_mat'),
                                                    ('spmT_images',
                                                     '2nd_lv_smoothed_avgcond.@T'),
                                                    ('con_images',
                                                     '2nd_lv_smoothed_avgcond.@con')]),
                    (level2thresh, datasink, [('thresholded_map',
                                               '2nd_lv_smoothed_avgcond.@threshold')])
                     ])

analysis2nd.config["execution"]["crashfile_format"] = "txt"
analysis2nd.run('MultiProc', plugin_args={'n_procs': 7})