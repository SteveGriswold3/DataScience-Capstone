import requests
import pickle
import time
from bs4 import BeautifulSoup
import datetime

def get_review_ids(soup):
    '''
    Doc Stings
    Convert the request content into a string to extract the data-review-id on the yelp page.
    
    INPUT:  Beautiful soup lxml
    OUTPUT: list of data review ids from Yelp page
    '''
    soup_string = str(soup)
    data_review_ids = []
    x = soup_string.find('data-review-id')
    next_id=x
    while next_id > 0:

        y=x+soup_string[x:100+x].find('"')
        z=y+soup_string[y+1:100+y].find('"')

        data_review_id = soup_string[y+1:z+1]
        if data_review_id not in data_review_ids:
            data_review_ids.append(data_review_id)

        next_id = soup_string[x+1:].find('data-review-id')

        x += next_id+1 
        if x>1:
            x+=1
            
    return data_review_ids

def save_data(reviews_dict, business_dict):
        with open('../data/yelp_review.pickle', 'wb') as pickleWriter:
            pickle.dump(reviews_dict, pickleWriter, protocol=2)

        with open('../data/yelp_businesses.pickle', 'wb') as pickleWriter:
            pickle.dump(business_dict, pickleWriter, protocol=2)
        
        print('Data saved Successfully!  Nice Work')
        pass
        
def append_review(soup, review_id_list, reviews_dict):
    '''
    Doc Stings
    Convert the request content into a string to extract the data-review-id on the yelp page.
    
    INPUT: 
    review_id_list: List of Review Ids from Yelp
    reviews_dict: Dictionary for storing Reviews
    OUTPUT: return the updated dictionary
    '''
    for review in review_id_list:
        div = soup.find("div", {"data-review-id": review})
        if div!=None:
            if div.find("p").text != '\n            Was this review …?\n    ':
                reviews_dict[review] = div.find("p").text

    return reviews_dict

class Download_Reviews(object):
    def __init__(self):
        with open('../data/yelp_businesses.pickle', 'rb') as pickleReader:
            self.business_dict = pickle.load(pickleReader)

        self.business_ids = [k for k, v in self.business_dict.items() if v['location']['state']=='AZ' ]

        with open('../data/yelp_review.pickle', 'rb') as pickleReader:
            self.reviews_dict = pickle.load(pickleReader)

        self.nbr_key= 0
        for bid in self.business_ids:
            if 'reviews_pulled' in self.business_dict[bid].keys():
                self.nbr_key += 1
        
        print('Keys Completed:', self.nbr_key, 'of', len(self.business_ids))

        self.ds = open('../data/data_scraping.txt', 'a')
        pass

    def run_dl(self, number_to_pull):
        try:
            while self.nbr_key < (number_to_pull + self.nbr_key):
                if 'reviews_pulled' not in self.business_dict[self.business_ids[self.nbr_key]].keys():
                    url = self.business_dict[self.business_ids[self.nbr_key]]['url']
                    r = requests.get(url)

                    print('Key:', self.nbr_key)
                    print('Request Status:', r.status_code)
                    if r.status_code == 200:
                        time.sleep(45)
                        soup = BeautifulSoup(r.content, "lxml")

                        review_ids_list = get_review_ids(soup)

                        self.reviews_dict = append_review(soup, review_ids_list, self.reviews_dict)

                        self.business_dict[self.business_ids[self.nbr_key]]['reviews_pulled'] = True
                    
                    if self.ds.closed:
                        self.ds = open('../data/data_scraping.txt', 'a')
                        print('opened data scraping log file.')
                    self.ds.write("{date}\t{key}\t{status}\n".format(date=datetime.datetime.now(), key=self.nbr_key, status=r.status_code))
                    
                    print(self.business_ids[self.nbr_key] , 'Done', self.business_dict[self.business_ids[self.nbr_key]]['reviews_pulled'])
                    print(len(self.reviews_dict), 'done')

                self.nbr_key += 1
                print('Next Key:', self.nbr_key, 'to', (number_to_pull + self.nbr_key))
            
            print('Batch Done at Key:', self.nbr_key)
            save_data(self.reviews_dict, self.business_dict)
            pass

        finally:
            print('Error')
            save_data(self.reviews_dict, self.business_dict)
            self.ds.close()

        pass

        
