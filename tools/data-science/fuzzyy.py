# takes a list of words
# compares each word to the following words in this list via fuzzywuzzy
# if the words are quite similar (>90) it prints both words and the ratio


from fuzzywuzzy import fuzz
import pandas as pd
import glob
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

output = []
for csvfile in glob.glob('./mostFreqWords/' + 'trainingset.csv'):
    wordlist = pd.read_csv(csvfile)
    for index, row in wordlist.iterrows():
        for wordindex in range(index + 1, len(wordlist)):
            ratio = fuzz.ratio(row['word'], wordlist['word'][wordindex])
            if ratio > 90:
                output.append([row['word'], wordlist['word'][wordindex], ratio])
    filename = csvfile[16:]
    output_df = pd.DataFrame(output, columns=['word1', 'word2', 'ratio'])
    output_df.to_csv('./output_sets/' + 'fuzzywords' + filename, index=False)
