# mft_vignettes
Code accompanying the paper: Moral Foundations Elicit Shared and Dissociable Cortical Activation Modulated by Political Ideology

## Directory Structure 

Directory structure follows the analysis presented in the manuscript. 

- behavior:
    - `beh_vignettes.ipynb` describes sample statistics and performs preprocessing + descriptive analysis on behavorial reponse data 
    - `lme_vignettes.html` R code for running linear mixed-effect models for moral judgment and response times
    
- glm:
    - `first_lv.py` nipype pipeline for performing first-level GLM in SPM12 on preprocessed vignettes 
    - `first_lv.sh` bash code for distributing nipype across HPC 
    - `second-lv.ipynb` code for running second-level (group) t-tests for GLM contrasts 
    - `surfplot.ipynb` code visualizing SPMs on cortical surfaces via surfplot
    
- mvpa:
    - `prepbetas.ipynb` code for extracting beta estimates from first-level SPMs 
    - `run_mvpa.ipynb` code for all MVPA decoding analyses
    
- rsa:
    - `rsa.ipynb` code for running the representational similarity analysis. 
    
- pol_mft
    - `ideology_beh.ipynb` code for regression analyses predicting responses to Moral Foundation Questionnaire and Moral Foundation Vignettes from political orientation 
    - `ideology_neural.ipynb` code for generating and visualizing cluster peaks from t-maps.