import pandas as pd


class DataImporter:
    def __init__(self, dataset):
        self.data = dataset
        self.get_df()

    def get_df(self):
        self.random_data = pd.read_csv(self.data, encoding='utf-8')

    def get_dtype(self):
        self.columns = self.random_data.columns[self.random_data.dtypes == 'float64']
        
    def fill_na(self):
        self.get_dtype()
        for column in self.columns:
            self.random_data[column].fillna(0, inplace=True)
            # print(self.random_data[column].isnull().sum())
        self.random_data['categories'].fillna('Undefined', inplace=True)
        self.random_data['product_name'].fillna('Undefined', inplace=True)

    def preprocess_too_high_values(self):
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

        :param column:
        :return:
        '''
        self.fill_na()
        for counter, column in enumerate(self.columns):
            if column != 'energy-kcal_100g':
                df = self.random_data[self.random_data[column] > 100]
                print(df)
                if counter == 0:
                    df.to_csv('data/out.csv', mode='a', index=False, encoding='utf-8')
                else:
                    df.to_csv('data/out.csv', mode='a', header=False, index=False, encoding='utf-8')
        # df = pd.read_csv('data/out.csv', header=False, encoding='utf-8')
        # print(df)

    def split_quant_qual(self, qual, quant_from, quant_to):
        self.fill_na()
        self.qualitative = self.random_data[qual]
        self.quantitative = self.random_data.loc[:, quant_from: quant_to]

        return self.quantitative, self.qualitative

    def get_true_df(self):
        self.fill_na()
        return self.random_data

    def save_new_dataset(self):
        self.fill_na()
        self.random_data.to_csv('out.csv')

'''
USAGE

d = DataImporter('data/preprocess_data.csv')
print(d.split_quant_qual(['Unnamed: 0', 'url', 'categories'], 'proteins_100g', 'nutrition-score-fr_100g'))
'''
d = DataImporter('data/preprocess_data.csv')
d.preprocess_too_high_values()
