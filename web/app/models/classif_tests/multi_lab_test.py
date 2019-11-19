# IMPORTS

import pandas as pd
import re
import pickle

# CONSTS

sgd = pickle.load(open("models_saves/SGDClassifier.pkl", 'rb'))
lr = pickle.load(open("models_saves/LogisticRegression.pkl", 'rb'))
mn = pickle.load(open("models_saves/MultinomialNB.pkl", 'rb'))

count_vect = pickle.load(open("models_saves/count_vect.pkl", 'rb'))
multilabel_binarizer = pickle.load(open("models_saves/multilabel_binarizer.pkl", 'rb'))
tfidf_transformer = pickle.load(open("models_saves/tfidf_transformer.pkl", 'rb'))

# FUNCTIONS

def strip_html_tags(body):
    regex = re.compile('<.*?>')
    body = body.lower()
    return re.sub(regex, '', body)


# VALUE TEST
df_test = pd.DataFrame(columns=['abstract'])
df_test["abstract"] = ["We study the direct and inverse scattering problem for the semilinear Schrödinger equation Δu+a(x,u)+k2u=0 in ℝd. We show well-posedness in the direct problem for small solutions based on the Banach fixed point theorem, and the solution has the certain asymptotic behavior at infinity. We also show the inverse problem that the semilinear function a(x,z) is uniquely determined from the scattering data. The idea is certain linearization that by using sources with several parameters we differentiate the nonlinear equation with respect to these parameter in order to get the linear one."]


df_test['abstract'] = df_test['abstract'].apply(strip_html_tags)

test_data = count_vect.transform(df_test.abstract)
test_data = tfidf_transformer.transform(test_data)

results = {}
i = 0
names = ["SGDClassifier", "LogisticRegression", "MultinomialNB"]

for model in [sgd, lr, mn]:
    res = model.predict(test_data)
    test = []
    for x in range(0, len(res)):
        temp = []
        for index, value in enumerate(res[x]):
            if value == 1:
                temp.append(multilabel_binarizer.classes_[index])
        test.append(temp)
    results[names[i]] = test
    i += 1

#print(res)
print(results)
