# this is the main class for the system to identify progression stages in patient diagnosis sequences
# it takes in a raw text file, parses the data, clusters the sequences, then segments the sequences in each cluster
# in the future, the final portion - in which the hidden stages are inferred - will be added

import sys
import parser
import clusterer
import segmenter
import matrix_creator as mc
from os import listdir
from os.path import isfile, join, basename


def main():
    data_dir = sys.argv[1]

    # first parse the input data to get the diagnosis and time sequences
    diag_sequences, time_sequences = parse_input_data(data_dir)

    # then create the similarity and distance matrices (only need to do this once)
    sim_mat, dist_mat = create_matrices(data_dir, diag_sequences)

    # if all of the files are already created and you are running the system again, you can comment the lines above
    # and uncomment these below to save time:
    #diag_sequences = open(data_dir + 'diag_sequences.txt', 'r').readlines()
    #for i in range(len(diag_sequences)):
     #   diag_sequences[i] = diag_sequences[i].replace('\n', '')
    #sim_mat_file = data_dir + 'sim_matrix.txt'
    #dist_mat_file = data_dir + 'dist_matrix.txt'
    #sim_mat = create_matrix_from_string(sim_mat_file)
    #dist_mat = create_matrix_from_string(dist_mat_file)

    # then cluster the sequences based on similarity
    cluster_dir = create_clusters(data_dir, diag_sequences, time_sequences, sim_mat, dist_mat)

    # then segment the sequences in the cluster directory
    segment_clusters(str(cluster_dir))


# go through the input data and parse through to create separate files of the diagnosis sequences and their respective
# time sequences
def parse_input_data(data_dir):
    input_data = open(data_dir + 'data.txt', 'r')
    input_lines = input_data.readlines()
    ps = parser.Parser(data_dir)
    diag_sequences, time_sequences = ps.create_diag_sequences(input_lines)
    diag_out_file = open(data_dir + 'diag_sequences.txt', 'w')
    for diag_sequence in diag_sequences:
        diag_out_file.write(str(diag_sequence) + '\n')

    time_out_file = open(data_dir + 'time_seqences.txt', 'w')
    for time_sequence in time_sequences:
        time_out_file.write(str(time_sequence) + '\n')

    return diag_sequences, time_sequences


# creates similarity and distance matrices of the diagnosis sequences based on the Longest Common Subsequence
def create_matrices(data_dir, input_sequences):
    sequences = []

    for line in input_sequences:
        sequences.append(line)

    mat = mc.MatrixCreator()
    sim_mat, dist_mat = mat.create_similarity_distance_matrix(sequences)
    sim_mat_out_file = open(data_dir + 'sim_matrix.txt', 'w')
    for list in sim_mat:
        sim_mat_out_file.write(str(list) + '\n')
    dist_mat_out_file = open(data_dir + 'dist_matrix.txt', 'w')
    for list in dist_mat:
        dist_mat_out_file.write(str(list) + '\n')

    return sim_mat, dist_mat


# creates clusters of similar diagnosis sequences using Affinity Propagation
# returns the directory of the clusters to be used for segmenting
def create_clusters(data_dir, input_sequences, time_sequences, sim_mat, dist_mat):
    c = clusterer.Clusterer(data_dir, input_sequences, time_sequences)
    cluster_dir = c.create_clusters_affinity(sim_mat, dist_mat)
    return cluster_dir


# segments the diagnosis sequences in each cluster by using a taxonomy tree of the ICD-9 codes to determine similarity
# similar codes that are close to each other (based on time) are put together
def segment_clusters(cluster_dir):
    s = segmenter.Segmenter()
    input_files = [f for f in listdir(cluster_dir) if isfile(join(cluster_dir, f))]

    for input_file in input_files:
        file_name = basename(input_file)
        # ignore all of the non cluster files in the folder
        if 'Store' in file_name or 'segmented' in file_name or 'counts' in file_name or 'cluster' not in file_name:
            continue
        cluster_number = file_name.replace('cluster', '')
        cluster_number = cluster_number.replace('.txt', '')
        input_seqs = open(join(cluster_dir, input_file), 'r').readlines()
        output_file = open(cluster_dir + 'segmented' + cluster_number + '.txt', 'w')

        average_time = s.get_average_time(input_seqs)
        s.create_output_segments(input_seqs, output_file, average_time)


# this method creates matrices from text files if they are already created
def create_matrix_from_string(matrix_file):
    matrix_string = open(matrix_file, 'r').readlines()
    list_mat = []
    for line in matrix_string:
        list_line = []
        line = line.replace("[", "")
        line = line.replace("]", "")
        line = line.replace("\n", "")
        line = line.strip("'")
        split_line = line.split(", ")
        for item in split_line:
            list_line.append(float(item))
        list_mat.append(list_line)
    return list_mat


if __name__ == '__main__':
    main()
