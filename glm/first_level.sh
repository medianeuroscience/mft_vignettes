#!/bin/bash
#SBATCH --partition=mnl-all
#SBATCH --array=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=7
#SBATCH --exclude=easley,wood,nash,ada,cox
#SBATCH --job-name=GLM
#SBATCH --output=/srv/lab/fmri/mft/fhopp_diss/analysis/vignettes/glm/scripts/logs/subject_%a.out

whoami && \
echo "Running job on: $SLURM_JOB_NODELIST" && \
docker run --rm --tty -v /srv/lab/fmri/mft/fhopp_diss/:/home/fhopp/spm -u fhopp:lab medianeuro/niflow python -u /home/fhopp/spm/analysis/vignettes/glm/spm/notebooks/first_level.py -subject $(printf %02d $SLURM_ARRAY_TASK_ID)
