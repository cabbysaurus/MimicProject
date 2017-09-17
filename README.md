# MimicProject
UCSD Internship Project using unsupervised methods to determine progression stages of patient sequences.

To run:

main.py runs the entire system (that has been developed thus far) for all of the patient data. It takes in a single argument, namely the folder in which the data is stored. Note that the data.txt file should be formatted as so:

89329 "6823"-1,0 "34889"-1,263 -2

The first number is the patient id, each number in quotes is an unformatted ICD-9 code, the numbers after the commas refer to the days (based on initial admission) on which the code was recorded, and the -1 and -2 are extraneous.

kidney_patients.py reads in all of the data from ADMISSIONS.csv and creates sequences based just on those patients with chronic kidney disease. The folders are hard coded in, but can be changed to point where you need.
