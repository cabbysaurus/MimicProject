# this is a class to go through all of the patients and pull out those who have a diag code for kidney disease
# look through all of the diags (not just primary) for kidney disease then build a file of diags and times for those patients

import pandas as pd
import numpy
import datetime
import parser

# codes for the six stages of chronic kidney disease
diag_codes = ['585.1', '585.2', '585.3', '585.4', '585.5', '585.6'] #, '585.9']
input_dir = '../UCSDInternship/data/'
admit_file = pd.read_csv(input_dir + 'ADMISSIONS.csv')
diagnoses_data = pd.read_csv(input_dir + "DIAGNOSES_ICD.csv")


# just go through the original data file and pull out the matching patient ids
def output_kidney_disease_info(kd_patients):
    input_file = open('data/data.txt', 'r')
    output_file = open('data/kd_data.txt', 'w')
    input_lines = input_file.readlines()

    for line in input_lines:
        split_line = line.split(' ')
        patient = split_line[0].strip()
        if patient in kd_patients:
            output_file.write(line)


# output the information for all of the kidney disease admissions
def output_kidney_disease_admits(patient, diag_file, time_file, cluster_file):
    diag_codes = []
    times = []
    patient_rows = admit_data[admit_data['SUBJECT_ID'] == patient]
    patient_rows.sort_values('HADM_ID')
    admissions = patient_rows['HADM_ID'].tolist()
    first_admit = int(admissions[0])

    for adm_id in admissions:
        adm_id = int(adm_id)
        kd = check_for_kidney_disease(adm_id)
        if kd:
            diag = parser.Parser.clean_diag_icd_code(get_primary_diag(adm_id))
            # if it's the first code, make the timespan 0
            if len(diag_codes) == 0:
                time = 0
            else:
                time = get_timespan(first_admit, adm_id)
            times.append(time)
            diag_codes.append(diag)

    diag_file.write(str(diag_codes) + '\n')
    time_file.write(str(times) + '\n')
    cluster_file.write(str(diag_codes) + '\t' + str(times) + '\n')


# calculate the timespan between two admissions
def get_timespan(adm1, adm2):
    admit1 = admit_file[admit_file['HADM_ID'] == adm1]
    admit2 = admit_file[admit_file['HADM_ID'] == adm2]
    date1 = get_date(admit1)
    date2 = get_date(admit2)
    day_difference = date2 - date1
    timespan = day_difference.days
    return timespan


# get the date as a datetime for an admission
def get_date(admit):
    row = admit.iloc[0]
    start = row['ADMITTIME']
    split_text = start.split(' ')
    date = split_text[0]
    split_date = date.split('-')
    year = int(split_date[0])
    month = int(split_date[1])
    day = int(split_date[2])
    return datetime.date(year, month, day)


# get the primary diagnosis code for an admission
def get_primary_diag(adm_id):
    diagnoses = diagnoses_data[diagnoses_data['HADM_ID'] == adm_id]
    diagnoses.sort_values('SEQ_NUM')
    primary_diag_row = diagnoses.iloc[0]
    primary_diag = primary_diag_row['ICD9_CODE']
    return primary_diag


# get a list of all the patients who have 2 or more hospital admissions with chronic kidney disease as one of the
# diagnoses codes for that admission
def get_kidney_disease_patients():
    patients = admit_data['SUBJECT_ID'].unique()
    kd_patients = []
    admits = []
    for patient in patients:
        patient_rows = admit_data[admit_data['SUBJECT_ID'] == patient]
        admissions = patient_rows['HADM_ID'].tolist()
        kd_count = 0
        for adm_id in admissions:
            kd = check_for_kidney_disease(adm_id)
            if kd:
                kd_count += 1
                if adm_id not in admits:
                    admits.append(adm_id)

            if kd_count >= 2 and patient not in kd_patients:
                kd_patients.append(str(patient))
                break
    print(str(len(kd_patients)))
    return kd_patients, admits


# goes through all of the diagnoses to see if any of them are in the list of kidney disease diagnosis codes
def check_for_kidney_disease(adm_id):
    diag_rows = diagnoses_data[diagnoses_data['HADM_ID'] == adm_id]
    diagnoses = diag_rows['ICD9_CODE'].tolist()
    for diagnosis in diagnoses:
        diagnosis = parser.Parser.clean_diag_icd_code(diagnosis)
        if diagnosis in diag_codes:
            return True
    return False


if __name__ == '__main__':
    # first get all the patients
    admit_data = admit_file.groupby('SUBJECT_ID').filter(lambda x: len(x) > 1)
    kd_patients, admits = get_kidney_disease_patients()

    diag_file = open('data/kidney_diag_sequences.txt', 'w')
    time_file = open('data/kidney_time_sequences.txt', 'w')
    cluster_file = open('data/kidney_cluster.txt', 'w')
    kidney_admit_file = open('data/kd_data/admits.txt', 'w')
    kidney_admit_file.write((str(admits)))

    # then go through each patient, get only the diags that have kidney disease as one of the codes, and output the
    # sequences to a text file
    for patient in kd_patients:
        patient = numpy.int64(patient)
        output_kidney_disease_admits(patient, diag_file, time_file, cluster_file)