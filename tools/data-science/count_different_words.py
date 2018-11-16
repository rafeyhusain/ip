# reads the corpussets and counts how often each word appears, prints out list with word and the count
# comment the stemming part, if the corpusset is already preprocessed


import pandas as pd
from nltk.stem.snowball import SnowballStemmer
from collections import Counter
from nltk.corpus import stopwords
import glob
import sys
import re

reload(sys)
sys.setdefaultencoding("utf-8")

st = SnowballStemmer("english")

for file in glob.glob('./corpussets/' + '*set.csv'):
    wordlist = pd.read_csv(file)
    wordlist = wordlist['masterbrain']
    for i in range(0, len(wordlist)):
        print wordlist[i]
        print type(wordlist[i])
        wordlist[i] = re.sub('[^a-zA-Z]', ' ', wordlist[i])  # _0-9 if want to leave digits
        words = [st.stem(word) for word in wordlist[i].split(' ') if
                 len(word) > 3 and word not in set(stopwords.words('english'))]
        wordlist[i] = ' '.join(words)

    string = wordlist.str.cat()
    mostcommon = Counter(string.split()).most_common()
    output = file[13:]
    output = '-'.join(w for w in output)
    output = output.split('.')[0]

    output_df = pd.DataFrame(mostcommon, columns=['word', 'number'])
    output_df.to_csv('./mostFreqWords/' + output, index=False)
