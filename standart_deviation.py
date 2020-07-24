from sklearn.cluster import DBSCAN
import numpy as np
import pandas as pd

random_data = pd.read_csv('data/preprocess_data.csv')

labels = random_data[['Unnamed: 0', 'url', 'categories']]
random_data = random_data.loc[:, 'proteins_100g': 'nutrition-score-fr_100g']

random_data = random_data.fillna(0)

# print(random_data.columns)
# print(random_data.isnull().sum(axis=0))

outlier_detection = DBSCAN(min_samples=2, eps=3)
clusters = outlier_detection.fit_predict(random_data)
print(list(clusters).count(-1))
