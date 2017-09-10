# this class handles separating the events of an entire sequence into segments
import icd_tree as it


class Segmenter(object):

    def __init__(self):
        self.tree = it.IcdTree('icd_tree.txt')
        # these are the thresholds for distance and time respectively. distance is the exponential distance between
        # two nodes based on the taxonomy tree. the time threshold is the factor by which to multiply
        self.max_dist = 5
        self.time_thresh = 1.9

    @staticmethod
    def clean_sequence(sequence):
        sequence = sequence.replace('[', '')
        sequence = sequence.replace(']', '')
        sequence = sequence.replace('\\', '')
        split_sequence = sequence.split(', ')
        clean_sequence = []
        for item in split_sequence:
            item = item.strip()
            clean_sequence.append(item)
        return clean_sequence

    def segment_sequence_lca_exp_dist(self, sequence, time_sequence, average_time, output_file):
        try:

            min_dist = self.max_dist
            original_sequence = []
            for i in range(len(sequence)):
                item = sequence[i].strip("'")
                original_sequence.append(item)
            while min_dist <= self.max_dist:
                if 'None' in sequence:
                    break
                temp_sequence = []
                i = 0
                min_i = None
                min_lca = None
                while i < len(sequence) - 1:
                    current = sequence[i].strip("'")
                    next = sequence[i+1].strip("'")
                    #time_current = int(time_sequence[i].replace("'", ""))
                    #time_next = int(time_sequence[i+1].replace("'", ""))

                    # if the events occur far from each other, then don't put them together. what is far though???
                    #if abs(time_next - time_current) < average_time  * self.time_thresh:
                    #    i += 1
                    #    continue

                    lca, exp_dist = self.tree.get_lca_exponential_distance(current, next)
                    if exp_dist < min_dist:
                        min_dist = exp_dist
                        min_i = i
                        min_lca = lca
                    i += 1

                if min_i is None:
                    return sequence
                j = 0
                while j < len(sequence):
                    if j != min_i:
                        temp_sequence.append(sequence[j])#.strip("'")
                    else:
                        temp_sequence.append(min_lca)
                        #segment = []
                        #segment.append(original_sequence[j])#.strip("'")
                        #segment.append(original_sequence[j+1])#.strip("'")
                        #print(str(original_sequence), str(len(original_sequence)))
                        #original_sequence[j] = segment
                        original_sequence[j] = str(original_sequence[j]) + ' ' + str(original_sequence[j+1])
                        original_sequence.pop(j+1)
                        j += 1
                    j += 1

                sequence = temp_sequence
                min_dist = self.max_dist
            return str(original_sequence)

        finally:
            output_file.write(str(original_sequence) + '\n')


    @staticmethod
    def get_average_time(input_seqs):
        total_time = 0
        amount_time = 0

        for seq in input_seqs:
            split_seq = seq.split('\t')
            time = split_seq[1]
            split_time = time.split(',')
            for item in split_time:
                item = item.replace("'", "")
                item = item.replace("[", "")
                item = item.replace("]", "")
                item = item.strip()
                time = int(item)
                total_time += time
                amount_time += 1

        average_time = total_time / amount_time
        print(str(average_time))
        return average_time

    def create_output_segments(self, input_seqs, output_file, average_time):
        for seq in input_seqs:
            split_seq = seq.split('\t')
            diags = split_seq[0]
            times = split_seq[1]
            if diags == "['']":
                continue
            clean_sequence = self.clean_sequence(diags)
            time_sequence = self.clean_sequence(times)
            self.segment_sequence_lca_exp_dist(clean_sequence, time_sequence, average_time, output_file)
            #output_file.write(str(segmented_sequence) + '\n')


