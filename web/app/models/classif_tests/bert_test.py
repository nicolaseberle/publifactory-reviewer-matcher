# IMPORTS

import torch
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from ast import literal_eval
import gensim.parsing.preprocessing as gsp

# FUNCTIONS

filters = [
           gsp.strip_tags,
           gsp.strip_punctuation,
           gsp.strip_multiple_whitespaces,
           gsp.strip_numeric,
           gsp.remove_stopwords
          ]

def strip_html_tags(body):
    body = str(body)
    for f in filters:
        body = f(body)
    body = body.lower()
    return body


# MAIN

df = pd.read_csv('../w2v/abstract_fields_subcat_200K.csv')
df = df[:20000]

df['text'] = df['abstract'].apply(strip_html_tags)
df['fields'] = [x.replace('_', '') for x in df['fields']]
df['fields'] = [literal_eval(x) for x in df['fields']]

multilabel_binarizer = MultiLabelBinarizer()
multilabel_binarizer.fit(df.fields)
Y = multilabel_binarizer.transform(df.fields)

df['labels'] = tuple(Y)
for x in range(0, len(multilabel_binarizer.classes_)):
    df[multilabel_binarizer.classes_[x]] = [y[x] for y in df['labels']]

train_df, eval_df = train_test_split(df, test_size=0.2)

test_df = eval_df

model = torch.load('outputs/pytorch_model.bin')

to_predict = test_df.text
preds, outputs = model.predict(to_predict)

sub_df = pd.DataFrame(outputs, columns=['artandhumanities', 'biology', 'businessandeconomics', 'chemistry',
                                        'computerscience','earthandplanetarysciences', 'engineering',
                                        'environmentalscience', 'healthprofession', 'materialsscience',
                                        'mathematics', 'medicine', 'multidisciplinary', 'neuroscience', 'nursing',
                                        'physics', 'psychology', 'sociology'])

print(sub_df.head())
