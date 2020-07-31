import pandas as pd
import statistics
from scipy import spatial


class DataImporter:
    def __init__(self, dataset):
        self.data = dataset
        self.get_df()

    def get_df(self):
        '''
        load dataset
        :return:
        '''
        self.random_data = pd.read_csv(self.data, encoding='utf-8')

    def get_float_column(self):
        '''
        select float column
        :return:
        '''
        self.columns = self.random_data.columns[self.random_data.dtypes == 'float64']
        
    def fill_na(self):
        '''
        fill na:
        by 0 for float column
        by string for object column
        :return:
        '''
        self.get_float_column()
        for column in self.columns:
            self.random_data[column].fillna(0, inplace=True)
            # print(self.random_data[column].isnull().sum())
        self.random_data['categories'].fillna('Undefined', inplace=True)
        self.random_data['product_name'].fillna('Undefined', inplace=True)

    def preprocess_too_high_values(self):
        '''
        Find high values by column
        compare the product to the other from the same categories without the too high values column
        remove or correct them
        :return:
        '''

        '''
        Données issues de la Table de composition nutritionnelle Ciqual 2012 réalisée par l'Agence nationale de sécurité sanitaire de l'alimentation, de l'environnement et du travail (Anses).
        Les aliments les plus riches en protéines sont:
         les gélatines alimentaires qui en comportent 87.60g/100g
         les levures alimentaires 48g/100/
         le parmersan 38.60g/100g
         suivit d'une centaine de plats de viandes ou emmental 37.40g ~ 25g/100g
         au moins 1400 produits en dessous du seul des 25g/100g

        Les aliment les plus riches en fat sont:
         les huiles, graisses et le saindoux 100g/100g
         la margarine, le beurre doux et le beurre demi-sel sont eux à 84.40g ~ 80.80g/100g
         il y a près de 200 produits (chipolata, chocolat, tomme, mayonaises..) au dessus de 25g/100g
         au moins 1300 produits en dessous du seul des 25g/100g

        Les aliment les plus riches en saturated-fat sont:
         pain de friture 92.60g/100g
         noix de coco, amandes seches 57.10g/100g
         les beurres 54.90g ~ 37.40g/100g
         il y a près de 20ènes produits (chocolats et fromages) au dessus de 25g. 33.40g ~ 26.30g/100g

        Les aliment les plus riches en sodium sont:
         sel 39,10g/100g
         Bouillon de légumes déshydraté  13,200g/100g
         Sauce de soja 6,260g/100g
         Anchois à l’huile 4,450g/100g
         moutardes 2.360g/100g

        Les aliment les plus riches en carbohydrates (glucides) sont:
         fructose 399,80g/100g
         les sucres  99.60 ~ 96.70g/100g
         chewing-gum 92g/100g
         et plus de 330 autres aliments (liqueurs, gateaux de riz, pizzas, cheeseburgers, sirots, barres de chocolats, petit dej, plats préparé, préparations et poudres...) au dessus de 25g/100g

        Les aliment les plus riches en sel sont:
         sel 39,10g/100g
         Bouillon de légumes déshydraté  19,100g/100g
         sauce soja 6.26g/100g
         Jambons crûs, fumé, poisson marinés 2,360g/100g
         Anchois à l’huile 4,450g/100g
         moutardes 2.360g/100g
         4 produit au dessus de 25g/100g

        Les aliment les plus riches en sucre sont:
         fructose 99.80g/100g
         les sucres 99g/100g
         bonbons, chocolats, miels 90g/100g
         fruits sec 60g/100g
         confitures 55g/100g
         une centaines de produits, préparations sucré chocolaté a udesssu de 25g/100g

        Les aliment les plus riches en fibre sont:
         cannelle, coriandre 43.50g/100g
         poudres chocolat, curry, chicoré 40g/100g
         thym 30g/100g
         poivre et café en poudre 25g ~20g/100g
         confitures 55g/100g
         une 10ène de produits, préparations sucré chocolaté a udesssu de 25g/100g        
        '''

        self.fill_na()

        # preparer les dicts des index à traiter
        _res = {}
        _keeped = {}

        '''
        traiter les cas de value error        
        traiter energy-kcal       
        '''
        try:
            for counter, column in enumerate(self.columns):
                if column != 'energy-kcal_100g':

                    # traiter les valeurs trop elevé ( > 100 )
                    df = self.random_data[self.random_data[column] > 100]

                    ## DEBUG
                    # print(df[column], column)
                    # save_column = df[column]
                    ##

                    # prendre les données sans la column en cour de traitement
                    df = df.loc[:, df.columns != column]
                    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # print tout la ligne de donnees
                        for index in df.index:

                            ## DEBUG
                            # print('------------')
                            # print(save_column[save_column.index == index])
                            # print(df[df.index == index])
                            ##

                            # creer un jeu de donnees de comparaison temporaire base sur la categories du produit cible
                            tmp_data = self.random_data[self.random_data['categories'].str.contains(df[df.index == index]['categories'].values[0])].loc[:, self.random_data.columns != column]
                            # supprimer la ligne contenant la donnee cible du jeu de comparaison
                            tmp_data = tmp_data.drop(index)

                            ## DEBUG
                            # print(df.loc[index]['url'])
                            # print('\n')
                            ##

                            # preparer une list pour stocker les valeurs des produits similaires
                            _toMean = []
                            for _ in range(5):
                                # calculer la similarite
                                ary = spatial.distance.cdist(tmp_data.loc[:, tmp_data.dtypes == 'float64'], df.loc[:, df.dtypes == 'float64'], metric='euclidean')
                                try:
                                    # creer un score pour choisir si de remplacer ou supprimer
                                    _score = 0

                                    ## DEBUG
                                    # print(f'{column}::         {save_column[save_column.index == index].values[0]} / {self.random_data[self.random_data.index.values == tmp_data[ary == ary.min()].index.values][column].values[0]}')
                                    ##

                                    # selectionner la ligne similaire
                                    tmp_row = tmp_data[ary == ary.min()]

                                    # comparer les valeurs de chaques column  comparaison / cible
                                    for _column in self.columns:
                                        if _column != column:
                                            _val = df[df.index == index][_column].values[0]
                                            _compare = tmp_row[_column].values[0]

                                            ## DEBUG
                                            # print(f'{_column}::         {_val} / {_compare}')
                                            ##

                                            # etendre la zone de verification a + 10% - 10%
                                            _up, _down = self.get_around_values(_val, _column)

                                            # incrementer le score si la valeur compare est comprise dans le spectre
                                            if _down <= _compare <= _up:
                                                _score += 1

                                    # ajouter la valeur compare pour un calcul du mean
                                    _toMean.append(self.random_data[self.random_data.index.values == tmp_data[ary == ary.min()].index.values][column].values[0])

                                    ## DEBUG
                                    # print('\n*********\n')
                                    ##

                                    # ajouter l'index a supprimer
                                    if _score < len(self.columns) - 1:
                                        '''
                                        remplacer l'ancienne valeur par la mmoyenne des autres
                                        '''
                                        _res[index] = ''

                                        ## DEBUG
                                        # print('NOT MODIFY', index)
                                        # print(save_column[save_column.index == index].values[0])
                                        # print(self.random_data[self.random_data.index.values == tmp_data[ary == ary.min()].index.values][column].values[0])
                                        ##

                                    # drop la ligne deja traiter pour ne pas boucler sur la meme comparaison a chaque fois
                                    tmp_data = tmp_data.drop(tmp_row.index)

                                    ## DEBUG
                                    # print(_res, len(_res))
                                    ##

                                except:
                                    '''
                                    library python debuger :: pdb 
                                    afficher la categorie et la column cibler, le nombre aussi.
                                    '''
                                    print('-')
                                    _res[index] = ''

                                # calculer le mean puis remplacer la valeur, supprimer l'index des index a supprimer
                                try:
                                    if _toMean and _score >= len(self.columns) - 1:

                                        ## DEBUG
                                        # print('MODIFY', index)
                                        # print(_toMean)
                                        ##

                                        _meaned = statistics.mean(_toMean)

                                        ## DEBUG
                                        # print(_meaned)
                                        # print(self.random_data[self.random_data.index == index][column])
                                        ##

                                        # update avec le mean
                                        self.random_data.at[self.random_data.index == index, column] = _meaned

                                        ## DEBUG
                                        # print(self.random_data[self.random_data.index == index][column])
                                        ##

                                        del _res[index]
                                        _keeped[index] = ''

                                except:
                                    pass
                                '''
                                 check si les autres valeurs sont egales, si elles le sont, modifier la valeurs de la column cible pour qu'elle soit le mean a celle comparer ::
                                 !! ne pas faire : sinon verifier si la valeur de la column cible est egale a la valeur comparer || diviser par 10,100
                                 si non modifie, supprimer et tenir le compte.
                                  !!!
                                  Verifier les cas qui reviennent en valueerror except 
                                  !!!
                                '''

                            print('------------\n')

        except ValueError as e:
            print(e)
            '''
            library python debuger :: pdb 
            '''

        ## DEBUG
        # print(_res, len(_res))
        # print(_keeped, len(_keeped))
        ##

        # drop les lignes non modifiables
        for ids in _res:
            self.random_data.drop(index=ids, inplace=True)



        # save le new dataset
        self.save_new_dataset()

    def split_quant_qual(self, qual, quant_from, quant_to):
        '''
        DEBUG affichage
        :param qual:
        :param quant_from:
        :param quant_to:
        :return:
        '''
        self.fill_na()
        self.qualitative = self.random_data[qual]
        self.quantitative = self.random_data.loc[:, quant_from: quant_to]

        return self.quantitative, self.qualitative

    def save_new_dataset(self):
        '''
        save the new dataset
        :return:
        '''
        self.random_data.to_csv('data/preprocess_data2.csv', index=False, encoding='utf-8')

    @staticmethod
    def get_around_values(value, col, percent=90):
        '''
        return la valeur haute ( valeur + percent ) et la valeur basse ( valeur - percent )
        :param value:
        :param col:
        :param percent:
        :return:
        '''
        _up = [100.00 if col != 'energy-kcal_100g' and round(value + (value - ((percent * value) / 100.0)), 2) > 100 else round(value + (value - ((percent * value) / 100.0)), 2)][0]
        _down = round(value - (value - ((percent * value) / 100.0)), 2)
        return _up, _down

    def print_tester(self):
        '''
        look for the most similar row
        comparer avec les aliments de la meme categorie
        '''
        self.fill_na()
        '''
        presenter le probleme du jeu de donnée eronée 
        ne pas traiter les valeurs en dessous de 100 pour ce projet
        '''
        with pd.option_context('display.max_columns', None):  # print tout la ligne de donnees
            _tmp_row = self.random_data[['energy-kcal_100g', 'proteins_100g', 'carbohydrates_100g', 'fat_100g', 'alcohol_100g','product_name']].sort_values(by='energy-kcal_100g', ascending=False)
            _tmp_row['estimated_kcal_100g'] = (_tmp_row['proteins_100g'] * 4) + (_tmp_row['carbohydrates_100g'] * 4) + (_tmp_row['fat_100g'] * 9) + (_tmp_row['alcohol_100g'] * 7)
            _up, _down = self.get_around_values(_tmp_row['estimated_kcal_100g'], 'energy-kcal_100g', 70)

            result = f"{_tmp_row[['energy-kcal_100g', 'product_name', 'estimated_kcal_100g']]}, {_tmp_row[_tmp_row['energy-kcal_100g'].between(_down, _up)]}"
            print(result)
            self.to_text('data/error_kcal.txt', result)

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

'''
USAGE

d = DataImporter('data/preprocess_data.csv')
print(d.split_quant_qual(['Unnamed: 0', 'url', 'categories'], 'proteins_100g', 'nutrition-score-fr_100g'))
'''
# d = DataImporter('data/preprocess_data.csv')
d = DataImporter('data/preprocess_data2.csv')
# d.preprocess_too_high_values()
d.print_tester()


'''
regarder s'il y a des valeurs manquantes, des données aberantes comme des boulette de viandes à 0 kcal par exemple. 
'''