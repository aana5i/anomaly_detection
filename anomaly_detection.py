# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pylab
pylab.rcParams.update({'font.size': 14})

preprocess_data_path = 'data/preprocess_data2.csv'


class ProcessDataset:
    def __init__(self, preprocess_data_path):
        self.df = pd.read_csv(preprocess_data_path, encoding='utf-8')  # importation du CSV

    @staticmethod
    def to_text(path, data, mode='a', encoding='utf-8'):
        '''
        save to text
        :param path:
        :param data:
        :param mode:
        :param encoding:
        :return:
        '''
        _encoding = ['utf-8', 'shift_jis']
        with open(path, mode, encoding=[_encoding[encoding] if isinstance(encoding, int) else encoding][0]) as f:
            f.write(data)

    # def drop_high_value(self):
    #     self.df = self.df.drop(index=309192)  #drop la value trop élévé de proteins

    def prepare_dataset(self):
        '''
        sauvegarder les variables qualitatives variables (ID, categories)
        sauvegarder les variables quantitatives
        :return:
        '''
        # variables qualitatives
        self.qualitative = self.df['Unnamed: 0']
        self.urls = self.df[['url', 'categories']]
        self.product_names = self.df[['product_name']]

        # variables quantitatives
        self.data = self.df.loc[:, 'proteins_100g': 'energy-kcal_100g']
        # self.data = self.data.fillna(0)

    def process_data(self):
        '''

        :return:
        '''
        self.prepare_dataset()
        self.params = [column for column in self.data.columns]
        self._done = []  # garder

        for param in self.params:
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
            self.get_product_near_quantiles(qv1, qv2, qv3, param)
            self.print_product_names()

            # gen plot
            # self.gen_boxplot(param)
            # self.gen_hist(param)
            self.gen_pairplot(param)

    # créer le box plot
    # les moustaches sont les calculs (qv1 - dv_limit (limité à la valeur min du jeu de données)) et (dv3 + dv_limit)
    def gen_boxplot(self, param):
        fig = pylab.figure(figsize=(4, 6))
        ax = fig.add_subplot(1, 1, 1)
        for y in self.outliers_data: # zip name
            ax.text(1, y, '')
        ax.boxplot(self.data[param])
        ax.set_ylabel(param)
        plt.figtext(1, 0.5, f'{self.result_text}', horizontalalignment='left')
        plt.figtext(-0.1, 0.1, f'{self.pname_result}', horizontalalignment='right')
        plt.savefig(f'save_plot/{param}-boxPlot.png', bbox_inches="tight")
        # plt.show()
        '''
        faire un boxplot de tout et un séparé pour chaque
        '''

    def gen_hist(self, param):
        fig, ax = plt.subplots()
        ax.hist(self.data[param], density=True, bins=30, range=(0, self.data[param].max() + 10))
        ax.set_title(param)
        # ax.set_xlabel('/100g')
        # ax.set_ylabel('%')
        plt.figtext(1, 0.4, f'{self.result_text}', horizontalalignment='left')
        plt.figtext(-0.1, -0.1, f'{self.pname_result}', horizontalalignment='right')
        plt.savefig(f'save_plot/{param}-histPlot.png', bbox_inches="tight")

        # plt.show()
        '''
        faire un hist de tout et un séparé pour chaque
        '''

    def gen_pairplot(self, param):
        sns.set(style="ticks", color_codes=True)
        for column in self.params:
            if column != param and column not in self._done:
                tmp_data = self.data[[param, column]]
                sns.pairplot(tmp_data)
                plt.savefig(f'save_plot/pairPlot_{param}-{column}.png', bbox_inches="tight")
        self._done.append(param)

    def gen_full_data_set_pair_plot(self):
        self.prepare_dataset()
        sns.pairplot(self.data)
        plt.savefig(f'save_plot/pairPlot_data-set.png', bbox_inches="tight")

        '''
        prendre la valeur en carbohydrate, la mettre sur l'axe des ordonée du graphe, prendre la valeur des fibres pour l'axe des absysse 

        si ligne transversale, => correlation 
        ce pairplot  sert a reperrer des correlation        
        
        si "triangle" plus de ( partie occupé par les points ) que de l'autre partie globalement )
        '''

    def print_result(self, quantile, counter, param):
        result = ''
        tmp = []
        _key = ['qv1', 'qv2', 'qv3', '100']
        key = _key[counter]
        for qant in quantile:
            tmp.append(self.product_names.iloc[qant]['product_name'])
            result += f"-----------------------\n{self.p_name}" \
                f"\n{self.urls.iloc[qant]['categories']}" \
                f"\n{self.urls.iloc[qant]['url']}" \
                f"\n{self.data.iloc[qant]}" \
                f"\n-----------------------\n"
            key = self.data.iloc[qant][param]
        self.p_name[key] = tmp
        return result

    # afficher des produits proches des quantiles
    def get_product_near_quantiles(self, qv1, qv2, qv3, param):
        _list = [qv1, qv2, qv3, 100]
        self.p_name = {}
        for counter, _l in enumerate(_list):
            result = f'{param}\n{str(_l)}\n'
            _up, _down = self.get_around_values(_l)
            _num = self.data.index[self.data[param].between(_down, _up)].tolist()[:5]
            result += self.print_result(_num, counter, param)
            self.to_text(f'save_plot/quantiles.txt', result)

    def print_product_names(self):
        result = ''
        for k, v in self.p_name.items():
            result += f'{k}:\n'
            for _v in v:
                result += f'{_v}\n'
        self.pname_result = result

    @staticmethod
    def get_around_values(value, percent=90):
        _up = [100.00 if round(value + (value - ((percent * value) / 100.0)), 2) > 100 else round(value + (value - ((percent * value) / 100.0)), 2)][0]
        _down = round(value - (value - ((percent * value) / 100.0)), 2)
        return _up, _down


p = ProcessDataset(preprocess_data_path)
p.gen_full_data_set_pair_plot()

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