from sklearn.cluster import DBSCAN
from data_importer import DataImporter


d = DataImporter('data/preprocess_data.csv')

random_data, labels = d.split_quant_qual(['Unnamed: 0', 'url', 'categories'], 'proteins_100g', 'nutrition-score-fr_100g')
random_data = random_data.fillna(0)

outlier_detection = DBSCAN(min_samples=2, eps=3)
clusters = outlier_detection.fit_predict(random_data)
print(list(clusters).count(-1))

'''
DBScan Clustering:
DBScan is a clustering algorithm that’s used cluster data into groups. It is also used as a density-based anomaly detection method with either single or multi-dimensional data.
Other clustering algorithms such as k-means and hierarchal clustering can also be used to detect outliers.
In this instance, I will show you an example of using DBScan but before we start, let’s cover some important concepts. DBScan has three important concepts:
Core Points: In order to understand the concept of the core points, we need to visit some of the hyperparameters used to define DBScan job. First hyperparameter (HP)is min_samples.
This is simply the minimum number of core points needed in order to form a cluster. second important HP is eps.
eps is the maximum distance between two samples for them to be considered as in the same cluster.
Border Points are in the same cluster as core points but much further away from the centre of the cluster.
Image for post => Source:https://stackoverflow.com/questions/34394641/dbscan-clustering-what-happens-when-border-point-of-one-cluster-is-considered
Everything else is called Noise Points, those are data points that do not belong to any cluster.
They can be anomalous or non-anomalous and they need further investigation.

The output of the above code is 94. This is the total number of noisy points. SKLearn labels the noisy points as (-1).
The downside with this method is that the higher the dimension, the less accurate it becomes.
You also need to make a few assumptions like estimating the right value for eps which can be challenging.
'''
