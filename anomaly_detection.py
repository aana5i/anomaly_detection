# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import pylab
pylab.rcParams.update({'font.size': 14})

preprocess_data_path = 'data/preprocess_data.csv'


class ProcessDataset:
    def __init__(self, preprocess_data_path):
        self.df = pd.read_csv(preprocess_data_path, encoding='utf-8')  # importation du CSV
        self.drop_high_value()

    @staticmethod
    def to_text(path, data, mode='a', encoding='utf-8'):
        _encoding = ['utf-8', 'shift_jis']
        with open(path, mode, encoding=[_encoding[encoding] if isinstance(encoding, int) else encoding][0]) as f:
            f.write(data)

    def drop_high_value(self):
        self.df = self.df.drop(index=309192)  #drop la value trop élévé de proteins

    def prepare_dataset(self):
        # sauvegarder les variables qualitatives variables (ID, categories)
        self.qualitative = self.df['Unnamed: 0']
        self.urls = self.df[['url', 'categories']]
        self.product_names = self.df[['product_name']]
        # sauvegarder les variables quantitatives
        self.data = self.df.loc[:, 'proteins_100g': 'energy-kcal_100g']
        self.data = self.data.fillna(0)

    def process_data(self):
        self.prepare_dataset()

        params = [column for column in self.data.columns]
        for param in params:
            # trouver les quantiles et l’écart interquartile
            qv1 = self.data[param].quantile(0.25)
            qv2 = self.data[param].quantile(0.5)
            qv3 = self.data[param].quantile(0.75)
            qv_limit = 1.5 * (qv3 - qv1)  # indicateur d'écartement
            outliers_sum = (self.data[param] > (qv3 + qv_limit)).sum()

            # trouver la position des outliers et utiliser les variables qualitatives comme labels
            self.outliers_mask = (self.data[param] > qv3 + qv_limit) | (self.data[param] < qv1 - qv_limit)
            self.outliers_data = self.data[param][self.outliers_mask]
            self.outliers_name = self.qualitative[self.outliers_mask]

            # print("\n-----------------------")
            # print(f'sorting {param}')
            # print(data[param].sort_values(ascending=True))
            # print("-----------------------\n")

            first_row = f'first quarter: {qv1}\nfirst quarter - quarter limit: {qv1 - qv_limit}, {round((self.data[param] < qv1 - qv_limit).sum()/self.data[param].shape[0] * 100, 2)}%' #  25% des valeurs sont en dessous de la valeur du premier quartile
            second_row = f'second quarter: {qv2}'  #  50% des valeurs sont en dessous de la valeur du deuxieme quartile
            third_row = f'third quarter: {qv3} \nthird quarter + quarter limit: {qv3 + qv_limit}'  #  75% des valeurs sont en dessous de la valeur du troisieme quartile
            fourth_row = f'quarter limit: {qv_limit}'
            five_row = f'over q3+qv_limit: {outliers_sum}, {round(outliers_sum/self.data[param].shape[0] * 100, 2)}%'

            # print(data[param][outliers_mask == True].drop_duplicates().sort_values(ascending=True))

            self.result_text = f'{param}\n'
            self.result_text += f"-----------------------\n{first_row}\n{second_row}\n{third_row}\n{fourth_row}\n{five_row}\n-----------------------\n"

            self.to_text(f'save_plot/result-text.txt', self.result_text)
            self.gen_boxplot(param)
            self.gen_hist(param)
            self.get_product_near_quantiles(qv1, qv2, qv3, param)

    # créer le box plot
    # les moustaches sont les calculs (qv1 - dv_limit (limité à la valeur min du jeu de données)) et (dv3 + dv_limit)
    def gen_boxplot(self, param):
        fig = pylab.figure(figsize=(4, 6))
        ax = fig.add_subplot(1, 1, 1)
        for y in self.outliers_data: # zip name
            ax.text(1, y, '')
        ax.boxplot(self.data[param])
        ax.set_ylabel(param)
        plt.savefig(f'save_plot/{param}-boxPlot.png')
        # plt.show()
        '''
        faire un boxplot de tout et un séparé pour chaque
        '''

    def gen_hist(self, param):
        fig, ax = plt.subplots()
        ax.hist(self.data[param], density=True, bins=30, range=(0,110))
        ax.set_title(param)
        # ax.set_xlabel('/100g')
        # ax.set_ylabel('%')
        plt.savefig(f'save_plot/{param}-histPlot.png')
        plt.figtext(0.99, -0.4, f'{self.result_text}', horizontalalignment='right')
        # plt.show()
        '''
        faire un hist de tout et un séparé pour chaque
        '''

    def print_result(self, quantile):
        result = ''
        for qant in quantile:
            result += f"-----------------------\n{self.product_names.iloc[qant]['product_name']}" \
                f"\n{self.urls.iloc[qant]['categories']}" \
                f"\n{self.urls.iloc[qant]['url']}" \
                f"\n{self.data.iloc[qant]}" \
                f"\n-----------------------\n"
        return result

    # afficher des produits proches des quantiles
    def get_product_near_quantiles(self, qv1, qv2, qv3, param):
        _list = [qv1, qv2, qv3, 100]
        for _l in _list:
            result = f'{param}\n{str(_l)}\n'
            _num = self.data.index[self.data[param] == _l].tolist()[:5]
            result += self.print_result(_num)
            self.to_text(f'save_plot/quantiles.txt', result)


# df = pd.read_csv('data/preprocess_data.csv', encoding='utf-8')
#
# # drop the bad index after gen_boxplot  ne pas faire, on en est a detecter les anomalies ici
# # print(df.sort_values(by='proteins_100g', ascending=True))
# # print(df[df['Unnamed: 0'] == 786748]['proteins_100g'])
# df = df.drop(index=309192)  #drop la value trop élévé de proteins
#
# # sauvegarder les variables qualitatives variables (ID, categories)
# qualitative = df['Unnamed: 0']
# urls = df[['url', 'categories']]
# product_names = df[['product_name']]
# # sauvegarder les variables quantitatives
# data = df.loc[:, 'proteins_100g': 'energy-kcal_100g']
# data = data.fillna(0)
#
#
# # ANALYSES
# # Outliers Univarié
# # Créer un boxp lot des outlers univarié de 'proteins_100g'
# param = 'proteins_100g'
#
#
# def process_data(param):
#     # trouver les quantiles et l’écart interquartile
#     qv1 = data[param].quantile(0.25)
#     qv2 = data[param].quantile(0.5)
#     qv3 = data[param].quantile(0.75)
#     qv_limit = 1.5 * (qv3 - qv1)  # indicateur d'écartement
#     outliers_sum = (data[param] > (qv3 + qv_limit)).sum()
#
#     # trouver la position des outliers et utiliser les variables qualitatives comme labels
#     outliers_mask = (data[param] > qv3 + qv_limit) | (data[param] < qv1 - qv_limit)
#     outliers_data = data[param][outliers_mask]
#     outliers_name = qualitative[outliers_mask]
#
#     # print("\n-----------------------")
#     # print(f'sorting {param}')
#     # print(data[param].sort_values(ascending=True))
#     # print("-----------------------\n")
#
#     first_row = f'first quarter: {qv1}\nfirst quarter - quarter limit: {qv1 - qv_limit}, {round((data[param] < qv1 - qv_limit).sum()/data[param].shape[0] * 100, 2)}%' #  25% des valeurs sont en dessous de la valeur du premier quartile
#     second_row = f'second quarter: {qv2}'  #  50% des valeurs sont en dessous de la valeur du deuxieme quartile
#     third_row = f'third quarter: {qv3} \nthird quarter + quarter limit: {qv3 + qv_limit}'  #  75% des valeurs sont en dessous de la valeur du troisieme quartile
#     fourth_row = f'quarter limit: {qv_limit}'
#     five_row = f'over q3+qv_limit: {outliers_sum}, {round(outliers_sum/data[param].shape[0] * 100, 2)}%'
#
#     # print(data[param][outliers_mask == True].drop_duplicates().sort_values(ascending=True))
#
#     result_text = f'{param}\n'
#     result_text += f"-----------------------\n{first_row}\n{second_row}\n{third_row}\n{fourth_row}\n{five_row}\n-----------------------\n"
#     print(result_text)
#
# def to_text(path, data, mode='a', encoding='utf-8'):
#     _encoding = ['utf-8', 'shift_jis']
#     with open(path, mode, encoding=[_encoding[encoding] if isinstance(encoding, int) else encoding][0]) as f:
#         f.write(data)
#
#
# to_text(f'save_plot/result-text.txt', result_text)
#
# '''
# boucler pour chaque param et sauvegarder le tout dans un seul fichier texte
# '''
#
# # créer le box plot
# # les moustaches sont les calculs (qv1 - dv_limit (limité à la valeur min du jeu de données)) et (dv3 + dv_limit)
# def gen_boxplot():
#     fig = pylab.figure(figsize=(4, 6))
#     ax = fig.add_subplot(1, 1, 1)
#     for y in outliers_data: # zip name
#         ax.text(1, y, '')
#     ax.boxplot(data[param])
#     ax.set_ylabel(param)
#     plt.savefig(f'save_plot/{param}-boxPlot.png')
#     plt.show()
#     '''
#     faire un boxplot de tout et un séparé pour chaque
#     '''
#
# # gen_boxplot()
#
#
# def gen_hist():
#     fig, ax = plt.subplots()
#     ax.hist(data[param], density=True, bins=30, range=(0,110))
#     ax.set_title(param)
#     # ax.set_xlabel('/100g')
#     # ax.set_ylabel('%')
#     plt.savefig(f'save_plot/{param}-histPlot.png')
#     plt.figtext(0.99, -0.4, f'{result_text}', horizontalalignment='right')
#     plt.show()
#     '''
#     faire un hist de tout et un séparé pour chaque
#     '''
#
#
# def print_result(quantile):
#     result = ''
#     for qant in quantile:
#         result += f"-----------------------\n{product_names.iloc[qant]['product_name']}"\
#             f"\n{urls.iloc[qant]['categories']}" \
#             f"\n{urls.iloc[qant]['url']}" \
#             f"\n{data.iloc[qant]}" \
#             f"\n-----------------------\n"
#     return result
#
#
# # afficher des produits proches des quantiles
# def get_product_near_quantiles():
#     _list = [qv1, qv2, qv3, 100]
#     for _l in _list:
#         result = f'{param}\n{str(_l)}\n'
#         _num = data.index[data[param] == _l].tolist()[:5]
#         result += print_result(_num)
#         to_text(f'save_plot/quantiles.txt', result)
#
#
# get_product_near_quantiles()
# process_data(param)

p = ProcessDataset(preprocess_data_path)
p.process_data()
'''
Se représenter les données en revenant à quelque chose de simple/schematique

!!! converser le nom du produit !!!

- Retrouver l'autre fichier.py ::
- Expliquer le pourquoi du retrait et de la conservation des colonnes.
- Rechercher les differents taux/pourcentage de matieres/colonnes par produits (proteins dans la viande blanche ~20%).
- Au dessus de 100 par 100g, c'est une erreur, découvrir pourquoi si beaucoup d'impact sur le jeu de données ou au contraire si peu de temps à investir.
- Catégoriser les produits selon leurs composants, ex: 20% de proteins ect ... OU Vérifier leurs catégories.
- Prendre des produits proches des quantiles pour se faire une idée de ce que représente le quantile => recherche google. 

- afficher le nombre de valeurs et le pourcentage que sa represente au dessus du 3em quartile ::
- Faire des Boxplot de chaque colonnes, les sauvegarder en PNG/JPEG.  ::
- Voir ce que représetent les données, outliers. 100% de sel dans du sel c'est normal.
- PairPlot deux par deux, si pas de corrélation le jeu de données est bon.
- BoxPlot => Hist: voir la forme de la distribution ( gaussienne: forme en cloche )


- Faire une interprétation concrète avec des points de repères par indicateur (ex: huile = 100% gras, beurre = 85% etc)
'''

'''
ajouter le nom des produits au dataset ::
'''