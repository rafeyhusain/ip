# takes trainingset and testset, preprocesses the data, runs multinomial bayes,
# prints out the cross validation accuracy scores


import pandas as pd
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
import re
import csv
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

train_set = pd.read_csv('./output_sets/Trainset.csv')
train_set = train_set[['category', 'masterbrain']]
train_set = train_set.dropna()

test_set = pd.read_csv('./output_sets/Testset.csv')
test_set = test_set[['category', 'masterbrain']]
test_set = test_set.dropna()

st = SnowballStemmer("english")

corpus_train = []
for i in range(0, len(train_set)):
    train_set.masterbrain[i] = re.sub('[^a-zA-Z]', ' ', train_set.masterbrain[i])  # _0-9 if want to leave digits
    words = [st.stem(word) for word in train_set.masterbrain[i].split(' ') if
             len(word) > 3 and word not in set(stopwords.words('english'))]
    train_set.masterbrain[i] = ' '.join(words)
    corpus_train.append(train_set.masterbrain[i])
print 'done preprocessing train set'

outputfile = "./corpussets/trainingset.csv"
with open(outputfile, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', lineterminator='\n')
    for row in corpus_train:
        writer.writerow([row])

corpus_test = []
for i in range(0, len(test_set)):
    test_set.masterbrain[i] = re.sub('[^a-zA-Z]', ' ', test_set.masterbrain[i])  # _0-9 if want to leave digits
    words = [st.stem(word) for word in test_set.masterbrain[i].split(' ') if
             len(word) > 3 and word not in set(stopwords.words('english'))]
    test_set.masterbrain[i] = ' '.join(words)
    corpus_test.append(test_set.masterbrain[i])
print 'done preprocessing test set'

outputfile = "./corpussets/testset.csv"
with open(outputfile, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', lineterminator='\n')
    for row in corpus_test:
        writer.writerow([row])

exit()

cv = CountVectorizer(max_features=1000)
cv.fit_transform(corpus_train).toarray()
X_train = cv.fit_transform(corpus_train).toarray()
y_train = train_set.iloc[:, 0].values
X_test = cv.transform(corpus_test).toarray()
y_test = test_set.iloc[:, 0].values

classifier = MultinomialNB(alpha=0.2)  # can change to anything from [0,1] for different smoothing
classifier.fit(X_train, y_train)
y_pred = classifier.predict(X_test)
accuracies = cross_val_score(estimator=classifier, X=X_train, y=y_train, cv=10)
crosstab = pd.crosstab(y_test, y_pred, rownames=['True'], colnames=['Predicted'], margins=True)
cm = confusion_matrix(y_test, y_pred)

print('accuracies:', accuracies)
print('avg accuracy:', sum(accuracies) / len(accuracies))
print ('accuracy score:', accuracy_score(y_pred, y_test))

outputfile = "./corpussets/snowball_200-2000_nodigits_morethan3.csv"
with open(outputfile, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', lineterminator='\n')
    writer.writerow(['accuracies:', accuracies])
    writer.writerow(['avg accuracy:', sum(accuracies) / len(accuracies)])
    writer.writerow(['accuracy score:', accuracy_score(y_pred, y_test)])
