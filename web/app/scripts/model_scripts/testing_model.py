import pickle

model = pickle.load(open("../pickles/model_v1.p", "rb" ))

# TESTING

#print(model_scripts.wv.similarity('breast', 'cancer'))
print(model.wv.most_similar(positive=['breast'], topn=10))
