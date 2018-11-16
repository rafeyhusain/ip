# takes the first 1000 products from each category productlist
# divide the data equally in 80% Trainingdataset and 20% Testdataset

import pandas as pd
import sys
import glob

reload(sys)
sys.setdefaultencoding("utf-8")

trainingset = './output_sets/Trainingset_thirdlevel.csv'
testset = './output_sets/Testset_thirdlevel.csv'
prodfile = './output_sets/numberOfProducts_thirdlevel.csv'

training_list = []
testing_list = []
product_count_list = []

# for file in glob.glob('./output/' + '*.csv'):
for file in glob.glob('./prodsthirdlevel/' + '*.csv'):
    df = pd.read_csv(file, delimiter=',')
    df = df.dropna(subset=['masterbrain'])
    df = df.dropna(subset=['brandName'])
    row_count = len(df)
    if row_count > 1000:
        row_count = 1000
    if row_count < 50:
        continue
    training_count = int(0.8 * row_count)
    test_count = row_count - training_count
    product_count_list.append([file, training_count, test_count])

    for index, row in df.iterrows():
        if training_count > 0:
            training_count = training_count - 1
            training_list.append([
                row['category_prefix'].split('/')[0] + "/",
                row['category_prefix'].split('/')[0] + "/" + row['category_prefix'].split('/')[1] + "/",
                row['category_prefix'].split('/')[0] + "/" + row['category_prefix'].split('/')[1] + "/" +
                row['category_prefix'].split('/')[2] + "/",
                row['masterbrain'],
                row['brandName']
            ])
        elif test_count > 0:
            test_count = test_count - 1
            testing_list.append([
                row['category_prefix'].split('/')[0] + "/",
                row['category_prefix'].split('/')[0] + "/" + row['category_prefix'].split('/')[1] + "/",
                row['category_prefix'].split('/')[0] + "/" + row['category_prefix'].split('/')[1] + "/" +
                row['category_prefix'].split('/')[2] + "/",
                row['masterbrain'],
                row['brandName']
            ])
        else:
            break

product_df = pd.DataFrame(product_count_list)
product_df.to_csv(prodfile, index=False, header=False)
training_df = pd.DataFrame(training_list,
                           columns=['cat_level_1', 'cat_level_2', 'cat_level_3', 'masterbrain', 'brandName'])
training_df.to_csv(trainingset, index=False)
testing_df = pd.DataFrame(testing_list,
                          columns=['cat_level_1', 'cat_level_2', 'cat_level_3', 'masterbrain', 'brandName'])
testing_df.to_csv(testset, index=False)
