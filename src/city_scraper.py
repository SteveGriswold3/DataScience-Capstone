import datetime
import numpy as np
import pandas as pd
import pickle
import pyspark as ps
import multiprocessing
import threading
import time
from timeit import Timer

from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client.yelp
yelp_bus = db.businesses
yelp_api_search = db.businessSearch
yelp_requests = db.requests
yelp_reviews = db.reviews

import psycopg2

from yelp_helpers import request
from yelp_helpers import load_api_key
key = load_api_key('../.gitignore/yelp_api_key.yaml')
API_KEY = key['client_secret']
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'

def convert_business_to_flat_dict(dict_value):
        new_dict = {}
        try_code = 'Failed'
        try:
            if 'id' in dict_value.keys():
                new_dict['id'] = dict_value['id']
            
            if 'name' in dict_value.keys():
                new_dict['name'] = (dict_value['name'])
            
            if 'image_url' in dict_value.keys():
                new_dict['image_url'] = (dict_value['image_url'])
            
            if 'url' in dict_value.keys():
                new_dict['url'] = (dict_value['url'])
            
            if 'review_count' in dict_value.keys():
                new_dict['review_count'] = (dict_value['review_count'])
            
            if 'categories' in dict_value.keys():
                new_dict['categories_alias'] = ([cat['alias'] for cat in dict_value['categories']])
                new_dict['categories_title'] = ([cat['title'] for cat in dict_value['categories']])
            
            if 'rating' in dict_value.keys():
                new_dict['rating'] = (dict_value['rating'])
            
            if 'coordinates' in dict_value.keys():
                new_dict['latitude'] = (dict_value['coordinates']['latitude'])
                new_dict['longitude'] = (dict_value['coordinates']['longitude'])
            
            if 'transactions' in dict_value.keys():
                new_dict['transactions'] = (dict_value['transactions'])
            
            if 'price' in dict_value.keys():
                new_dict['price'] = (dict_value['price'])
                
            if 'location' in dict_value.keys():
                new_dict['address1'] = (dict_value['location']['address1'])
                new_dict['address2'] = (dict_value['location']['address2'])
                new_dict['address3'] = (dict_value['location']['address3'])
                new_dict['city'] = (dict_value['location']['city'])
                new_dict['state'] = (dict_value['location']['state'])
                new_dict['zip_code'] = (dict_value['location']['zip_code'])
                new_dict['country'] = (dict_value['location']['country'])
                
            try_code = 'OK'
            return new_dict

        finally:
            if try_code == 'Failed':
                new_dict['Error'] = True
                return new_dict

class yelp_City_Scraper(object):
    '''
    Doc Strings:

    '''
    def __init__(self, latitude, longitude):
        '''
        Doc Strings:

        ring: Ring count from main latitude and longitude point.
        points: number of locations in the in the loop. points should be equal to loop x 2.
        jump: number to adjust the latitude and longitude, 0.1 is about 25 miles.  

        '''
        self.latitude = latitude
        self.longitude = longitude

        conn = psycopg2.connect(dbname='yelp', host='localhost')
        cur = conn.cursor()

        query = '''
                SELECT ring, points, jump
                FROM city
                WHERE latitude = {} and longitude = {};
                '''.format(latitude, longitude)
        
        cur.execute(query)
        print(type(cur))
        if len(cur.fetchall())==0:
            self.ring, self.points, self.jump = [1, 0, 0.025]
        else:
            self.ring, self.points, self.jump = cur.fetchone()

        conn.close()

        pass

    def save_progress(self):
        '''
        Saves the ring, points, and jump into scrapingProgress.txt.
        '''
        with open("data/scrapingProgress.txt", "w") as f:
            f.write(str(self.ring)+'\n')
            f.write(str(self.points)+'\n')
            f.write(str(self.jump)+'\n')
        pass

    
    def yelp_business_ring(self, latitude, longitude, radius=3225):
        '''
        Doc Strings:
        INPUT:
        longitude: decimal format.
        latitude: decimal format.
        radius:  yelp api only allows 1,000 business per location search.  If the radius returns greater not all the business can be obtained.

        OUTPUT: None.  Yelp scrapper class attributes are updated.
        '''
        conn = psycopg2.connect(dbname='yelp', host='localhost')
        cur = conn.cursor()

        if radius > 12874:
            radius = 12874
            print('radius can not be larger than 25 mile (12,874 meters.)')
            print('The radius has been reduced to avoid causing a yelp api error')
             
        url_params = {
                'latitude': latitude,
                'longitude': longitude,
                'radius': radius,
                'limit': 50
            }
        
        API_time = datetime.datetime.now()

        stat, Yelp_data = request(API_HOST, SEARCH_PATH, API_KEY, url_params=url_params)
        if stat!=200:
            print('Not 200 Status Code')
            print(Yelp_data)
            exit()

        API_data = {'{}_{}'.format(str(latitude).split('.'), str(longitude).split('.')): Yelp_data}
        yelp_api_search.insert(API_data)
        
        max_businesses = Yelp_data['total']
        print('Location business count: ', max_businesses)
        
        bus_list = []
        for business in Yelp_data['businesses']:
            # check business previously pulled
            query = '''
                    SELECT *
                    FROM businesses
                    WHERE businessid = '{}';
                    '''.format(business['id'])
            cur.execute(query)
            if len(cur.fetchall()) == 0:
                # zero means clear to load new business
                # add to mondo db
                bus_list.append(convert_business_to_flat_dict(business))
            
                # add business to sql
                query = '''
                        INSERT INTO businesses (businessid, reviews_pulled)
                        VALUES ('{}', 0);
                        '''.format(business['id'])
                #INSERT
                cur.execute(query)

        if len(bus_list)>0:            
            yelp_bus.insert_many(bus_list)
        
        time_diff = datetime.datetime.now()-API_time
        while time_diff.seconds < 5:
            time.sleep(1)
            time_diff = datetime.datetime.now()-API_time

        offset = 50

        while ((offset) < max_businesses) and (offset < 1000):
            url_params = {
                    'latitude': latitude,
                    'longitude': longitude,
                    'radius': radius,
                    'limit': 50,
                    'offset': offset
                }
            offset += 50
            
            API_time = datetime.datetime.now()

            stat, Yelp_data = request(API_HOST, SEARCH_PATH, API_KEY, url_params=url_params)

            if stat!=200:
                print('Not 200 Status Code:', stat)
                print(Yelp_data)
                exit()

            bus_list = []
            for business in Yelp_data['businesses']:
                # check business previously pulled
                query = '''
                        SELECT *
                        FROM businesses
                        WHERE businessid = '{}';
                        '''.format(business['id'])
                cur.execute(query)
                if len(cur.fetchall()) == 0:
                    # zero means clear to load new business
                    # add to mondo db
                    bus_list.append(convert_business_to_flat_dict(business))
                
                    # add business to sql
                    query = '''
                            INSERT INTO businesses (businessid, reviews_pulled)
                            VALUES ('{}', 0);
                            '''.format(business['id'])
                    #INSERT
                    cur.execute(query)

            if len(bus_list)>0:            
                yelp_bus.insert_many(bus_list)
                
            time_diff = datetime.datetime.now()-API_time
            while time_diff.seconds < 5:
                time.sleep(1)
                time_diff = datetime.datetime.now()-API_time
        
        print('adding to locations: {}, {}'.format(latitude, longitude))

        query = '''
                INSERT INTO locations (latitude, longitude, max_businesses)
                VALUES ({}, {}, {});
                '''.format(latitude, longitude, max_businesses)
        #INSERT
        cur.execute(query)
        conn.close()
        pass
    
    def previously_pulled(self, latitude,longitude):
        '''
        Doc Strings:
        INPUT:
        latitude:  float for latitude
        longitude:  float for longitude
        
        OUTPUT:
        True or False for previously pulled.
        '''
        conn = psycopg2.connect(dbname='yelp', host='localhost')
        cur = conn.cursor()

        query = '''
                SELECT * FROM locations
                WHERE latitude = {} and longitude = {};
                '''.format(latitude, longitude)
        #Retrieve
        cur.execute(query)
        response = (len(cur.fetchall()) > 0)

        conn.close()
        return response

    def scrape_rings(self, radius=3225):
        '''
        Doc Strings:
        INPUT:
        rings:  int for the number to expand out by the jump attribute.
        start_location:  tuple of the latitude, longitude.
        OUTPUT: updates files loging the history of scraping data.
        '''

        point_count = 0
        start_time = datetime.datetime.now()
        
        while 1 != 2:
            self.points += 2

            x = self.latitude - ((self.points/2)*self.jump)
            y = self.longitude + ((self.points/2)*self.jump)
            
            # North
            for n in range(self.points):
                if self.previously_pulled(x,y)==False:
                    self.yelp_business_ring(x, y, radius)
                x += self.jump

            point_count += n
            print('North Complete.  Elapsed Time: ', datetime.datetime.now()-start_time, 'Points:', point_count)

            # East
            for n in range(self.points):
                if self.previously_pulled(x,y)==False:
                    self.yelp_business_ring(x, y, radius)
                y -= self.jump
                
            point_count += n
            print('East Complete.  Elapsed Time: ', datetime.datetime.now()-start_time, 'Points:', point_count)

            # South
            for n in range(self.points):
                if self.previously_pulled(x,y)==False:
                    self.yelp_business_ring(x, y, radius)
                x -= self.jump

            point_count += n
            print('South Complete.  Elapsed Time: ', datetime.datetime.now()-start_time, 'Points:', point_count)

            # West
            for n in range(self.points):
                if self.previously_pulled(x,y)==False:
                    self.yelp_business_ring(x, y, radius)
                y += self.jump

            point_count += n
            print('West Complete.  Elapsed Time: ', datetime.datetime.now()-start_time, 'Points:', point_count)

            self.ring += 1

            # save progress
            conn = psycopg2.connect(dbname='yelp', host='localhost')
            cur = conn.cursor()

            query = '''
                    UPDATE city
                    SET ring = {}, points = {}
                    WHERE latitude = {} and longitude = {};
                    '''.format(self.ring, self.points, self.latitude, self.longitude)

            cur.execute(query)
            conn.close()
            
        pass
if __name__ == "__main__":
        print("main loaded")

