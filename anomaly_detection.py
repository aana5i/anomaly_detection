# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.svm import OneClassSVM
from sklearn.covariance import EllipticEnvelope
from pprint import pprint
import pylab

pylab.rcParams.update({'font.size': 14})


# importation du CSV
df = pd.read_csv('data/preprocess_data.csv')

# drop the bad index after gen_boxplot  ne pas faire, on en est a detecter les anomalies ici
# print(df.sort_values(by='proteins_100g', ascending=True))
# print(df[df['Unnamed: 0'] == 786748]['proteins_100g'])
df = df.drop(index=309192)

# sauvegarder les variables qualitatives variables (ID, categories)
qualitative = df['Unnamed: 0']
urls = df[['url', 'categories']]
# sauvegarder les variables quantitatives
data = df.loc[:, 'proteins_100g': 'energy-kcal_100g']
data = data.fillna(0)


# ANALYSES
# Outliers Univarié
# Créer un boxp lot des outlers univarié de 'proteins_100g'
param = 'proteins_100g'

# trouver les quantiles et l’écart interquartile
qv1 = data[param].quantile(0.25)
qv2 = data[param].quantile(0.5)
qv3 = data[param].quantile(0.75)
qv_limit = 1.5 * (qv3 - qv1)  # indicateur d'écartement
outliers_sum = (data[param] > (qv3 + qv_limit)).sum()

# trouver la position des outliers et utiliser les variables qualitatives comme labels
outliers_mask = (data[param] > qv3 + qv_limit) | (data[param] < qv1 - qv_limit)
outliers_data = data[param][outliers_mask]
outliers_name = qualitative[outliers_mask]

print(f'sorting {param}')
print(data[param].sort_values(ascending=True))

print('first quarter:', qv1, '\nfirst quarter - quarter limit:', qv1 - qv_limit, ' (0)')  #  25% des valeurs sont en dessous de la valeur du premier quartile
print('second quarter:', qv2)  #  50% des valeurs sont en dessous de la valeur du deuxieme quartile
print('third quarter:', qv3, '\nthird quarter + quarter limit:', qv3 + qv_limit)  #  75% des valeurs sont en dessous de la valeur du troisieme quartile
# print('third quarter - first quarter:', qv3 - qv1)
print('quarter limit:', qv_limit)
print('outliers sum:', outliers_sum, '/', f'{round(outliers_sum/data[param].shape[0] * 100, 2)}%')

# print(data[param][outliers_mask == True].drop_duplicates().sort_values(ascending=True))


# créer le box plot
# les moustaches sont les calculs (qv1 - dv_limit (limité à la valeur min du jeu de données)) et (dv3 + dv_limit)
def gen_boxplot():
    fig = pylab.figure(figsize=(4, 6))
    ax = fig.add_subplot(1, 1, 1)
    for y in outliers_data: # zip name
        ax.text(1, y, '')
    ax.boxplot(data[param])
    ax.set_ylabel(param)
    plt.savefig(f'save_plot/{param}.png')
    plt.show()


# gen_boxplot()


# afficher des produits proches des quantiles
def get_product_near_quantiles():
    qv1_5 = data.index[data[param] == qv1].tolist()[:3]
    qv2_5 = data.index[data[param] == qv2].tolist()[:3]
    qv3_5 = data.index[data[param] == qv3].tolist()[:3]
    print(qv1_5)
    print(qv2_5)
    print(qv3_5)
    for q1_5 in qv1_5:
        print(data.iloc[q1_5])



get_product_near_quantiles()

'''
Se représenter les données en revenant à quelque chose de simple/schematique

!!! converser le nom du produit !!!

- Retrouver l'autre fichier.py
- Expliquer le pourquoi du retrait et de la conservation des colonnes.
- Rechercher les differents taux/pourcentage de matieres/colonnes par produits (proteins dans la viande blanche ~20%).
- Au dessus de 100 par 100g, c'est une erreur, découvrir pourquoi si beaucoup d'impact sur le jeu de données ou au contraire si peu de temps à investir.
- Catégoriser les produits selon leurs composants, ex: 20% de proteins ect ... OU Vérifier leurs catégories.
- Prendre des produits proches des quantiles pour se faire une idée de ce que représente le quantile => recherche google. 

- afficher le nombre de valeurs et le pourcentage que sa represente au dessus du 3em quartile ::
- Faire des Boxplot de chaque colonnes, les sauvegarder en PNG/JPEG.
- Voir ce que représetent les données, outliers. 100% de sel dans du sel c'est normal.
- PairPlot deux par deux, si pas de corrélation le jeu de données est bon.
- BoxPlot => Hist: voir la forme de la distribution ( gaussienne: forme en cloche )


- Faire une interprétation concrète avec des points de repères par indicateur (ex: huile = 100% gras, beurre = 85% etc)
'''
