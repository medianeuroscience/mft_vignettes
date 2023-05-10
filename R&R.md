# R&R ToDo List 

This document captures all additional analysis that will be done for the R&R. 
The order of analysis is in line with the order of the paper. 

1. Produce unsmoothed single-trial and runwise beta estimates using GLM. 

2. Do MVPA again like in PNAS and place in the SI (using sklearn instead of nltools). 

3. Perform moral wrongness predictions: 
    3.1. Across all conditions (how well can we predict moral judgment?)
    3.2. Cross-decoding: Train PCR-LASSO (L. Chang) on all but one foundation, and then predict ratigns for left-out foundation. 
4. RSA:
    4.1. Repeat RSA with unsmoothed runwise beta estimates 
    4.2. Perform item-level RSA using correlation distance 
    
5. Political Ideology
    5.1. MVPA & RSA for Democrats and Republicans, what do we see??? 
    
6. ROIs...do we see very different results in MVPA & RSA if we use more locally constrained spheres? 