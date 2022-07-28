from glob import glob
import pandas as pd
import gensim

datapath_='../data/ecommerce/'
files = glob(datapath_+'data*.csv')
data = pd.concat([pd.read_csv(f, encoding='latin') for f in files],
                 ignore_index=True).dropna().reset_index(drop=True)

data['CustomerID'] = data.CustomerID.astype(int)
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'], format='%m/%d/%Y %H:%M')
data['Description'] = data.Description.str.lower()
data = data.sort_values(by=['CustomerID', 'InvoiceDate']).reset_index(drop=True)

def import_data():
    return data

def make_prod_index():
    stock_descrp = data[['StockCode', 'Description']].drop_duplicates(ignore_index=True)
    stock_descrip = {k:v for i, (k,v) in stock_descrp.iterrows()}
    return stock_descrip

def create_customer_sessions():
    data['InvoiceDateHr'] = data.InvoiceDate.dt.to_period('H')
    user_sessions = data.groupby(['CustomerID', 'InvoiceDateHr'], as_index=False).agg({'StockCode':'unique'})
    user_sessions = user_sessions[user_sessions.StockCode.apply(len) > 1].reset_index(drop=True)
    seq_fname='stock_sequences.txt'
    with open(datapath_+seq_fname, 'w') as f:
        for row in user_sessions.StockCode:
            f.write(' '.join(row))
            f.write('\n')
    return user_sessions[['CustomerID', 'StockCode']]

def read_corpus(corpus):
    for i, line in enumerate(corpus):
        tokens = gensim.utils.simple_preprocess(line)
        yield gensim.models.doc2vec.TaggedDocument(tokens, [i])