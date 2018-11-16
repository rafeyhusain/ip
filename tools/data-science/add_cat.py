import pandas as pd
import glob
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

for file in glob.glob('./mostFreqWords/corpus/' + '*.csv'):
    input_df = pd.read_csv(file)
    output = []
    header = ['word', 'number']
    for i, row in input_df.iterrows():
        if i > 10000:
            break
        output.append([row['word'], row['number']])
    for comparefile in glob.glob('./mostFreqWords/' + '*.csv'):
        compareinput_df = pd.read_csv(comparefile)
        category = comparefile[16:]
        category = category.split('.')[0]
        header.append(category)
        for element in output:
            if element[0] in compareinput_df['word'].tolist():
                listindex = compareinput_df[compareinput_df['word'] == element[0]].index[0]
                number = compareinput_df['number'][listindex]
                element.append(number)
            else:
                number = 0
                element.append(number)
    filename = file[23:]
    outputfile = './mostFreqWords/mfw_with_category/' + filename
    output_df = pd.DataFrame(output, columns=header)
    output_df.to_csv(outputfile, index=False)
