import re, requests, json
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from trafilatura import extract
from tqdm import tqdm
from multiprocessing import Pool

def get_merchant_info(pages, i):
    with open('../data/ecommerce/atome/merchants_info_{}.json'.format(i), 'w') as f:
        for new_page in pages:
            merchant_page = requests.get(new_page).text
            soup = BeautifulSoup(merchant_page, "html.parser")
            pattern = re.compile("^(https://)")
            for link in soup.find_all("a", href=pattern):
                merchant_site=None
                if "href" in link.attrs \
                        and 'atome' not in link.attrs["href"] \
                        and 'youtube' not in link.attrs["href"]:
                    merchant_site=link.attrs["href"]
                    break
            descrip = extract(merchant_page).split('\n', 1)[0]            
            merchant_info = {'atome_page': new_page,
                             'merchant_site': merchant_site,
                             'description': descrip,
                             'category': i
                            }
            json.dump(merchant_info, f)
            f.write("\n")
                    
# def get_merchants():
#     pages = []
#     page_url = 'https://www.atome.sg/sitemap'
#     pattern = re.compile("^(/paylater-merchants)")
#     html = requests.get(page_url).text
#     soup = BeautifulSoup(html, "html.parser")
#     for link in soup.find_all("a", href=pattern):
#         if "href" in link.attrs:
#             new_page ="https://www.atome.sg" + link.attrs["href"]
#             if new_page not in pages:
#                 pages.append(new_page)
#     return pages

# def chunks(lst, n):
#     for i in range(0, len(lst), n):
#         yield lst[i:i + n]

def get_merchants():
    merchants_categories = {}
    categories = [
            'beauty',
            'fashion',
            'homedecor',
            'babyandkids',
            'electronics',
            'sports',
            'lifestyle',
            'accessories',
        ]
    for c in categories:
        pages = []
        page_url = 'https://www.atome.sg/paylater-stores/{c}'.format(c=c)
        pattern = re.compile("^(/paylater-merchants)")
        html = requests.get(page_url).text
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=pattern):
            if "href" in link.attrs:
                new_page ="https://www.atome.sg" + link.attrs["href"]
                if new_page not in pages:
                    pages.append(new_page)
        merchants_categories[c] = pages
        
    return merchants_categories
        
if __name__ == "__main__":
    atome_merchants = get_merchants()
#     atome_merchants = list(chunks(atome_merchants, 100))
#     with Pool(processes=8) as pool:
#         results_ = [pool.apply_async(get_merchant_info, (list_,i,)) for i, list_ in enumerate(atome_merchants)]
#         _ = [res.get() for res in tqdm(results_)]

    with Pool(processes=8) as pool:
        results_ = [pool.apply_async(get_merchant_info, (list_,i,)) for i, list_ in atome_merchants.items()]
        _ = [res.get() for res in tqdm(results_)]