# TDSelection

Author:
 - Valentina Beretta
	
Co-authors:
 - Sebastien Harispe
 - Sylvie Ranwez
 - Isabelle Mougenot

TDSelection is a post-processing procedure that permits to select the true values among a set of conflicting ones when considering partial order among values, during truth discovery process, for the estimation of value confidences. In these cases we cannot select the values having the highest confidence as truth as done by existing truth discovery models because the highest confidence is always assigned to the most general value (supported by all the others). Therefore, we propose this selection procedure.

## EXPERIMENTS
For repeat the experiments you have to follow the following steps:

 - make sure that "Pyhton 3.4" is installed on your computer and use it to run the .py files 
 
## INPUTs:
 - download the datasets birthPlace at https://doi.org/10.6084/m9.figshare.4616071, genre at https://doi.org/10.6084/m9.figshare.3393706, Cellular Component at https://doi.org/10.6084/m9.figshare.3824412, Molecular Function at https://doi.org/10.6084/m9.figshare.4040607 and Biological Process at https://doi.org/10.6084/m9.figshare.4476632; then unzip the archive and put the folder contained the dataset that you want analyze (you can choose one predicate dataset at time) in the empty project folder named "datasets". In this way the obtained folder hierarchy is TDSelection/TDO/datasets/dataset_birthPlace/EXP/... .
 - download the required file folder at https://doi.org/10.6084/m9.figshare.5374903, unzip the archive and put it in the folder named "required_files" of the project. The obtained folder hierarchy is TDSelection/TDO/required_files/birthPlace/

 
## RUN the experiments
 - open the terminal and move in the "experiments" folder contained in the main project folder
 - write the following command line
	> python run_final_experiments.py 
  
## OUTPUTs:
 - all the results file will be stored in "results" located in the "TDSelection/TDO/" project folder.
 
