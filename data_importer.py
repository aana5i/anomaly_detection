import pandas as pd


class DataImporter:
    def __init__(self, dataset):
        self.data = dataset

    def get_df(self):
        self.random_data = pd.read_csv(self.data)
        
    def fill_na(self):
        self.get_df()
        self.random_data['proteins_100g'].fillna(0, inplace=True)
        self.random_data['fat_100g'].fillna(0, inplace=True)
        self.random_data['saturated-fat_100g'].fillna(0, inplace=True)
        self.random_data['sodium_100g'].fillna(0, inplace=True)
        self.random_data['fruits-vegetables-nuts-dried_100g'].fillna(0, inplace=True)
        self.random_data['carbohydrates_100g'].fillna(0, inplace=True)
        self.random_data['salt_100g'].fillna(0, inplace=True)
        self.random_data['sugars_100g'].fillna(0, inplace=True)
        self.random_data['fiber_100g'].fillna(0, inplace=True)
        self.random_data['energy-kcal_100g'].fillna(0, inplace=True)
        self.random_data['alcohol_100g'].fillna(0, inplace=True)
        self.random_data['nutrition-score-fr_100g'].fillna(100, inplace=True)
        self.random_data['categories'].fillna('Undefined', inplace=True)

    def split_quant_qual(self, qual, quant_from, quant_to):
        self.fill_na()
        self.qualitative = self.random_data[qual]
        self.quantitative = self.random_data.loc[:, quant_from: quant_to]

        return self.quantitative, self.qualitative

    def get_true_df(self):
        self.fill_na()
        return self.random_data


'''
USAGE

d = DataImporter('data/preprocess_data.csv')
print(d.split_quant_qual(['Unnamed: 0', 'url', 'categories'], 'proteins_100g', 'nutrition-score-fr_100g'))
'''
