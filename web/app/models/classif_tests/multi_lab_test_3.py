# IMPORTS

import pandas as pd
import re
import pickle

# CONSTS

mlp = pickle.load(open("models_saves/mlpclassifier.pkl", 'rb'))

count_vect = pickle.load(open("models_saves/count_vect_v3.pkl", 'rb'))
multilabel_binarizer = pickle.load(open("models_saves/multilabel_binarizer_v3.pkl", 'rb'))
tfidf_transformer = pickle.load(open("models_saves/tfidf_transformer_v3.pkl", 'rb'))

# FUNCTIONS

def strip_html_tags(body):
    regex = re.compile('<.*?>')
    body = body.lower()
    return re.sub(regex, '', body)


# VALUE TEST
df_test = pd.DataFrame(columns=['abstract'])
df_test["abstract"] = ["While 3-SAT is NP-hard, 2-SAT is solvable in polynomial time. Austrin, Guruswami, and Håstad established, in precise terms, that the transition from tractability to hardness occurs just after 2 [FOCS'14/SICOMP'17]. They showed that the problem of distinguishing k-CNF formulas that are g-satisfiable (i.e. some assignment satisfies at least g literals in every clause) from those that are not even 1-satisfiable is NP-hard if gk<12 and is in P otherwise. We study a generalisation of SAT on arbitrary finite domains, with clauses that are disjunctions of unary constraints, and establish analogous behaviour. Thus we give a dichotomy for a natural fragment of promise constraint satisfaction problems (PCSPs) on arbitrary finite domains."]


df_test['abstract'] = df_test['abstract'].apply(strip_html_tags)

test_data = count_vect.transform(df_test.abstract)
test_data = tfidf_transformer.transform(test_data)

res = mlp.predict(test_data)
res2 = mlp.predict_proba(test_data)

results = []
for index, value in enumerate(res[0]):
    if value == 1:
        results.append(multilabel_binarizer.classes_[index])

recap = {}
for index, value in enumerate(res[0]):
    recap[multilabel_binarizer.classes_[index]] = [res[0][index], res2[0][index]]

recap = sorted(recap.items(), key=lambda kv: kv[1][1], reverse=True)

print(recap)
print(results)
