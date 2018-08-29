import requests
import pickle
import time
from bs4 import BeautifulSoup
import datetime
import pymongo

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

def append_review(bus_id, soup, review_id_list, reviews_dict):
    '''
    Doc Stings
    Convert the request content into a string to extract the data-review-id on the yelp page.
    
    INPUT: 
    review_id_list: List of Review Ids from Yelp
    reviews_dict: Dictionary for storing Reviews
    OUTPUT: return the updated dictionary
    '''
    review_dict = {}
    for review in review_id_list:
        div = soup.find("div", {"data-review-id": review})
        if div!=None:
            if div.find("p").text != '\n            Was this review …?\n    ':
                review_dict['review_id'] = review
                review_dict['business_id'] = bus_id
                review_dict['rating'] = div.find('div', {'class': 'i-stars'})['title']
                review_dict['review'] = div.find("p").text
                reviews_dict[review] = review_dict

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
        run_status = 'OK'

        #Mongo Client
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client.yelp
        raw_web = db.requests

        try:
            done_mark = number_to_pull + self.nbr_key
            while self.nbr_key < done_mark:
                run_status = 'Runnning'
                if 'reviews_pulled' not in self.business_dict[self.business_ids[self.nbr_key]].keys():
                    bus_id = self.business_ids[self.nbr_key]
                    url = self.business_dict[bus_id]['url']
                    r = requests.get(url)

                    print('Key:', self.nbr_key)
                    print('Request Status:', r.status_code)
                    if r.status_code == 200:
                        HTML_dict = {}
                        HTML_dict[bus_id] = r.content
                        raw_web.insert_one(HTML_dict)

                        time.sleep(45)
                        soup = BeautifulSoup(r.content, "lxml")
                        review_ids_list = get_review_ids(soup)
                        self.reviews_dict = append_review(bus_id, soup, review_ids_list, self.reviews_dict)
                        self.business_dict[bus_id]['reviews_pulled'] = True
                        run_status = 'OK'

                    if self.ds.closed:
                        self.ds = open('../data/data_scraping.txt', 'a')
                        print('opened data scraping log file.')
                    self.ds.write("{date}\t{key}\t{status}\n".format(date=datetime.datetime.now(), key=self.nbr_key, status=r.status_code))
                    
                    print(bus_id , 'Done', self.business_dict[bus_id]['reviews_pulled'])
                    run_status = 'OK'
                    print(len(self.reviews_dict), run_status)

                self.nbr_key += 1
                print('Next Key:', self.nbr_key, 'to', done_mark)
            
            print('Batch Done at Key:', self.nbr_key)

        finally:
            if run_status == 'Runnning':
                print('Error while Running')
            save_data(self.reviews_dict, self.business_dict)
            self.ds.close()

        pass
