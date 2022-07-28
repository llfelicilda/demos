import pandas as pd
from collections import defaultdict
from multiprocessing import Pool
from tqdm import tqdm
import json

data_path='/Users/felicildaloveme/personal_projects/data/ecommerce/home-depot-product-search-relevance/'

def ngrams(tokens, MIN_N, MAX_N):
    n_tokens = len(tokens)
    for i in range(n_tokens):
        for j in range(i+MIN_N, min(n_tokens, i+MAX_N)+1):
            yield tokens[i:j]

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        
def make_ngram_prod_feats (i, nl, inverted_index, product_data):
    with open(data_path+'product_ngrams_{i}.json'.format(i=i), 'w') as f:
        for ngram in nl:
            for docId in inverted_index[ngram]:
                row = product_data.loc[docId]
                line = {
                    'ngram': ngram,
                    'docId': docId,
                    'title_cnt': row['cleaned_title'].split().count(ngram),
                    'description_cnt': row['cleaned_description'].split().count(ngram),
                    'attributes_cnt': row['cleaned_attributes'].split().count(ngram),
                }
                json.dump(line, f)
                f.write('\n')

                
if __name__ == "__main__":
    data = pd.read_pickle(data_path+'cleaned_train_data.pkl')
    product_data = data[['product_uid', 'cleaned_title', 'cleaned_description', 'cleaned_attributes']].drop_duplicates(subset=['product_uid']).reset_index(drop=True)

    corpus = product_data.apply(lambda row: ' '.join([row['cleaned_title'], 
                                                      row['cleaned_description'],
                                                      row['cleaned_attributes']
                                                     ]).split(), axis=1)
    inverted_index = defaultdict(set)

    for docid, c in enumerate(corpus):
        ngrams_list = [' '.join(i) for i in ngrams(c, 1, 3)]
        for word in ngrams_list:
            inverted_index[word].add(docid)

    ngram_lists = list(chunks(list(inverted_index.keys()), 1000))
    with Pool(processes=8) as pool:
        results_ = [pool.apply_async(make_ngram_prod_feats, (i,ngl,{k:v for k,v in inverted_index.items() if k in ngl},product_data,)) for i,ngl in enumerate(ngram_lists)]
        _ = [res.get() for res in tqdm(results_)]
    