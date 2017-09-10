# this class handles all of the methods and code needed to cluster the sequences based on their similarity

import os
from collections import defaultdict
from sklearn.cluster import AffinityPropagation
from sklearn.metrics import silhouette_samples, silhouette_score


class Clusterer(object):

    def __init__(self, input_dir, diag_sequences, time_sequences):
        self.input_dir = input_dir
        self.diag_sequences = diag_sequences
        self.time_sequences = time_sequences
        # this controls the similarity threshold for clustering
        self.preference = 0.6

    # outputs the clusters to separate text files and prints out some information about the clusters
    # only outputs clusters that have 20 or more sequences
    def output_cluster_info(self, labels, algorithm, matrix):
        n_clusters_ = len(set(labels))
        print('Estimated number of clusters: %d' % n_clusters_)

        silhouette_avg = silhouette_score(matrix, labels)
        print('the average silhouette score is: ' + str(silhouette_avg))
        sample_silhouette = silhouette_samples(matrix, labels)

        for i in range(n_clusters_):
            i_cluster_silhouette = sample_silhouette[labels == i]
            i_cluster_silhouette.sort()

            if len(i_cluster_silhouette) >= 20:
                pos_sil = 0.0
                num_pos_sil = 0
                for sil in i_cluster_silhouette:
                    if sil >= 0:
                        pos_sil += sil
                        num_pos_sil += 1
                try:
                    avg_pos_sil = pos_sil / num_pos_sil
                except ZeroDivisionError:
                    avg_pos_sil = None
                print(str(i),  'pos sil:' + str(num_pos_sil), str(avg_pos_sil))
                sum = 0.0
                for sil in i_cluster_silhouette:
                    sum += float(sil)
                sum /= len(i_cluster_silhouette)
                print(i, str(sum))

        list_labels = labels.tolist()
        clusters = defaultdict(list)

        for i in range(0, len(list_labels)):
            label = list_labels[i]
            clusters[label].append(i)

        output_dir = self.input_dir + algorithm
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for key in clusters.keys():
            if len(clusters[key]) >= 20:
                print(key, len(clusters[key]))
                outfile = open('{0}{1}/cluster{2}.txt'.format(self.input_dir, algorithm, str(key)), 'w')
                for value in clusters[key]:
                    outfile.write(str(self.diag_sequences[value]) + '\t' + str(self.time_sequences[value]) + '\n')

        return output_dir

    # clusters the sequences using Affinity Propagation and returns the directory in which the clusters are stored
    def create_clusters_affinity(self, sim_mat, dist_mat):
        af = AffinityPropagation(affinity='precomputed', preference=self.preference)
        params = af.get_params()
        print(str(params))
        af.fit(sim_mat)
        # this is a one dimensional numpy array storing the labels for each patient
        labels = af.labels_
        output_dir = self.output_cluster_info(labels, 'affinity', dist_mat)
        return output_dir
