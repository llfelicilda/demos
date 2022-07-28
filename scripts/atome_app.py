from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer, util
import torch, string, spacy, pickle

nlp = spacy.load('en_core_web_sm')
with open('../data/atome_merchants_inverted_index.pkl', 'rb') as handle:
    inverted_index = pickle.load(handle)
embedder = SentenceTransformer('multi-qa-mpnet-base-dot-v1')
descrip_embeddings = torch.load('../data/atome_descrip_embeddings.pt')
with open('../data/atome_merchant_lookup.pkl', 'rb') as handle:
    merchant_lookup = pickle.load(handle)

def process_text (s):
    s = s.translate(str.maketrans('', '', string.punctuation))
    doc = nlp(s)
    lm_txt = ' '.join([token.lemma_ for token in doc]).lower()
    return lm_txt

def process_and_search(query):
    matched_documents = set()
    for word in query.split():
        matches = inverted_index.get(word)
        if matches:
            matched_documents |= matches
    return matched_documents

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    args = {'errors': errors, 'results': {}}
    if request.method == "POST":
        query = request.form['query']
        texts = process_text(query)
        if texts:
            match_indx = list(process_and_search(texts))
            query_embedding = embedder.encode(texts, convert_to_tensor=True)
            search_embeddings = descrip_embeddings[match_indx]
            if len(match_indx) > 0:
                cos_scores = util.pytorch_cos_sim(search_embeddings, descrip_embeddings)[0]
                idx_scores = [(i,s+1) if i in match_indx else (i,s) for i,s in enumerate(cos_scores)]
            else: 
                cos_scores = util.pytorch_cos_sim(query_embedding, search_embeddings)[0]
                idx_scores = [(i,s) for i,s in zip(match_indx, cos_scores)]
            idx_scores = sorted(idx_scores, key=lambda tup: tup[1], reverse=True)

            results = [(merchant_lookup[idx], "{:.4f}".format(score)) for idx, score in idx_scores if score > idx_scores[0][1]/3]
#             results = [(merchant_lookup[idx], "{:.4f}".format(score)) for idx, score in idx_scores]
            
            args = {'errors': errors, 'Query': query, 'results': results}
        else:
            errors.append(
                "Not enough query"
            )
            args = {'errors': errors, 'URL': query}
        
    return render_template('index.html', **args)


if __name__ == '__main__':
    app.run(host='localhost', port='7777', debug=True)
