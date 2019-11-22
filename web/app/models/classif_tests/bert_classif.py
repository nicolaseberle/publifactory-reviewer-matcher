# IMPORTS

import pandas as pd
import numpy as np
import pickle


from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from simpletransformers.classification import MultiLabelClassificationModel

import gensim.parsing.preprocessing as gsp


from ast import literal_eval

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

# LOADING & CLEANING

print("open json")
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

print(df.head(10))

print("split")

train_df, eval_df = train_test_split(df, test_size=0.2)

print("classif")

model = MultiLabelClassificationModel('roberta', 'roberta-base', use_cuda=False, num_labels=18,
                                      args={'fp16': False, 'train_batch_size': 2, 'gradient_accumulation_steps': 16,
                                            'learning_rate': 3e-5, 'num_train_epochs': 3, 'max_seq_length': 512})

print("train")

model.train_model(train_df)

pickle.dump(model, open("models_saves/bert_model.pkl", 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

print("eval")

'''result, model_outputs, wrong_predictions = model.eval_model(eval_df)

print(result)
print(model_outputs)
print(wrong_predictions)'''


test_df = eval_df

to_predict = test_df.text
preds, outputs = model.predict(to_predict)

sub_df = pd.DataFrame(outputs, columns=['artandhumanities', 'biology', 'businessandeconomics', 'chemistry',
                                        'computerscience','earthandplanetarysciences', 'engineering',
                                        'environmentalscience', 'healthprofession', 'materialsscience',
                                        'mathematics', 'medicine', 'multidisciplinary', 'neuroscience', 'nursing',
                                        'physics', 'psychology', 'sociology'])

print(sub_df.head())