from sklearn.ensemble import IsolationForest
from data_importer import DataImporter
from pprint import pprint
import numpy as np

d = DataImporter('data/preprocess_data.csv')

random_data, labels = d.split_quant_qual(['Unnamed: 0', 'url', 'categories'], 'proteins_100g', 'nutrition-score-fr_100g')
print(random_data.isna().sum())

full_data = d.get_true_df()
print(full_data.isna().sum())

clf = IsolationForest(max_samples=100, random_state=1, contamination='auto')
preds = clf.fit_predict(random_data)

indexes = np.where(preds == -1)[0]
to_del_indexes = np.where(preds == 1)[0]

print(len(indexes))
df = full_data.drop(index=to_del_indexes)
df2 = full_data.drop(index=indexes)
df.to_csv('data/outliers_data.csv', encoding='utf-8-sig')
df2.to_csv('data/clean_data.csv', encoding='utf-8-sig')
print(len(df))


'''
Isolation Forest:
Isolation Forest is an unsupervised learning algorithm that belongs to the ensemble decision trees family. This approach is different from all previous methods. 
All the previous ones were trying to find the normal region of the data then identifies anything outside of this defined region to be an outlier or anomalous.
This method works differently. It explicitly isolates anomalies instead of profiling and constructing normal points and regions by assigning a score to each data point. 
It takes advantage of the fact that anomalies are the minority data points and that they have attribute-values that are very different from those of normal instances.
 This algorithm works great with very high dimensional datasets and it proved to be a very effective way of detecting anomalies.
Since this article is focusing on the implementation rather than the know-how, I will not go any further on how the algorithm works. 
However, the full details on how it works are covered in this paper.

This code will output the predictions for each data point in an array. If the result is -1, it means that this specific data point is an outlier.
 If the result is 1, then it means that the data point is not an outlier.
'''
