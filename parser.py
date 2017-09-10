# this class handles all of the data parsing to create sequences and matrices


class Parser(object):
    def __init__(self, data_dir):
        self.data_dir = data_dir

# go through the input text file and generate a list of sequences for each patient.
# for now just building a sequence of diagnoses codes and corresponding time sequences
    def create_diag_sequences(self, input_lines, truncated=True):
        diag_sequences = []
        time_sequences = []
        for line in input_lines:
            tokens = line.split(' ')
            diag_sequence = []
            time_sequence = []
            for i in range(1, len(tokens) - 1):
                token = tokens[i]
                split_token = token.split(',')
                diagnosis = split_token[0].replace('-1', '').replace('"', '').strip()
                diag_icd = self.clean_diag_icd_code(diagnosis)
                if truncated and '.' in diag_icd:
                    split_icd = diag_icd.split('.')
                    diag_icd = split_icd[0]
                diag_sequence.append(diag_icd)
                time = split_token[1]
                time_sequence.append(time)
            if len(diag_sequence) > 1:
                diag_sequences.append(diag_sequence)
                time_sequences.append(time_sequence)
        return diag_sequences, time_sequences

    # static method to format the icd code
    @staticmethod
    def clean_diag_icd_code(icd_code):
        str_code = str(icd_code)
        if str_code[0] == 'E':
            if len(str_code) > 4:
                str_code = str_code[:4] + '.' + str_code[4:]
        else:
            if len(str_code) > 3:
                str_code = str_code[:3] + '.' + str_code[3:]
        return str_code

    # creates the similarity and distance matrices for all patient diagnosis sequences
    def create_similarity_distance_matrix(self, sequences):
        sim_mat = [[0 for j in range(len(sequences))] for i in range(len(sequences))]
        dist_mat = [[0 for j in range(len(sequences))] for i in range(len(sequences))]
        for i, seq1 in enumerate(sequences):
            for j, seq2 in enumerate(sequences):
                similarity, distance = self.get_similarity_distance(seq1, seq2)
                sim_mat[i][j] = similarity
                dist_mat[i][j] = distance
            print(str(i))
        return sim_mat, dist_mat

    # calculates the similarity and distance between two diagnosis sequences based on the LCSS
    def get_similarity_distance(self, sequence1, sequence2):
        lcs = self.get_lcs(sequence1, sequence2)
        similarity = len(lcs) / min(len(sequence1), len(sequence2))
        distance = 1.0 - similarity
        return similarity, distance

    # finds and returns the longest common subsequence between two patient diagnosis sequences
    # https://rosettacode.org/wiki/Longest_common_subsequence#Python
    def get_lcs(self, a, b):
        lengths = [[0 for j in range(len(b) + 1)] for i in range(len(a) + 1)]
        # row 0 and column 0 are initialized to 0 already
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                if x == y:
                    lengths[i + 1][j + 1] = lengths[i][j] + 1
                else:
                    lengths[i + 1][j + 1] = max(lengths[i + 1][j], lengths[i][j + 1])
        # read the substring out from the matrix
        result = []
        x, y = len(a), len(b)
        while x != 0 and y != 0:
            if lengths[x][y] == lengths[x - 1][y]:
                x -= 1
            elif lengths[x][y] == lengths[x][y - 1]:
                y -= 1
            else:
                assert a[x - 1] == b[y - 1]
                result.append(a[x - 1])
                x -= 1
                y -= 1
        return result
