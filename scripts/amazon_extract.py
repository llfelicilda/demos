import json, ast
from random import choice, choices
from tqdm import tqdm
from glob import glob
from multiprocessing import Pool
from subprocess import check_output

datapath_='../data/ecommerce/'
fields=['asin', 'title', 'description', 
        'also_buy', 'bought_together', 'buy_after_viewing', 
        'brand', 'categories', 'price', 'salesRank']
buy_fields=['also_buy', 'bought_together', 'buy_after_viewing']

def parse(path):
    with open(path, 'r') as f:
        for line in f:

            l = ast.literal_eval(line)
            line = {k:v for k, v in l.items() if k in fields}
            for k in [itm for itm in fields if itm not in line.keys()]:
                try:
                    line[k]=l['related'][k]
                except Exception as e: 
                    line[k]=[] if k in buy_fields else None
            yield line
            
def getDF(fn_in):
    fn=fn_in.split('/')[-1]
    fn_out1=fn+'.json'
    fn_out=fn+'_seq.json'
    asins = []
    total=int(check_output(["wc", "-l", fn_in]).decode().split(' ')[1])
    with open(datapath_+fn_out, 'w') as f, open(datapath_+fn_out1, 'w') as f1:
        for d in tqdm(parse(fn_in), total=total):
            asin=d['asin']
            if asin not in asins:
                row = {
                    'asin':asin,
                    'title':d['title'],
                    'description':d['description'],
                    'brand':d['brand'],
                    'categories':d['categories'], 
                    'price':d['price'],
                    'salesRank':d['salesRank']
                }
                asins.append(asin)
                json.dump(row, f1)
                f1.write('\n')
            seq = set(d['also_buy']+d['bought_together']+d['buy_after_viewing'])
            if len(seq) > 1:
                f.write(' '.join(seq))
                f.write('\n')
                
if __name__ == "__main__":
    
    json_files = [f for f in glob(datapath_+'amazon_products*')]
    with Pool(processes=8) as pool:
        results_ = [pool.apply_async(getDF, (f_in,)) for f_in in json_files]
        _ = [res.get() for res in results_]