#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 13:21:45 2018

@author: Steve Griswold

"""
import os
import datetime
import time
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from src.yelp_helpers import request
from src.yelp_helpers import load_api_key


key = load_api_key('.gitignore/yelp_api_key.yaml')
API_KEY = key['client_secret']
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'

class Yelp_Scraper:
    def __init__(self, ):
        '''
        Doc Strings:

        ring: Ring count from main latitude and longitude point.
        points: number of locations in the in the loop. points should be equal to loop x 2.
        jump: number to adjust the latitude and longitude, 0.1 is about 25 miles.  

        '''
        if os.path.exists('data/scrapingProgress.txt'):
            with open("data/scrapingProgress.txt", "r") as f:
                self.ring = int(f.readline().rstrip("\n"))
                self.points = int(f.readline().rstrip("\n"))
                self.jump = float(f.readline().rstrip("\n"))
        else:
            with open("data/scrapingProgress.txt", "w") as f:
                f.write('1\n0\n.025')

        loc_list = np.loadtxt('data/loc_list.txt')
        self.loc_list = [x for x in loc_list]

        with open('data/yelp_businesses.pickle', 'rb') as pickleReader:
            self.business_dict = pickle.load(pickleReader)
        
        pass
    
    def get_progress(self):
        '''
        gets values from the scrapingProgress.txt file.
        '''

        with open("data/scrapingProgress.txt", "r") as f:
            self.ring = int(f.readline().rstrip("\n"))
            self.points = int(f.readline().rstrip("\n"))
            self.jump = float(f.readline().rstrip("\n"))
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

        stat, Yelp_data = request(API_HOST, SEARCH_PATH, API_KEY, url_params=url_params)
        if stat!=200:
            print('Not 200 Status Code')
            print(Yelp_data)
            exit()

        for business in Yelp_data['businesses']:
            self.business_dict[business['id']] = business
            
        time.sleep(5)

        max_businesses = Yelp_data['total']
        print('Location business count: ', max_businesses)
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
            
            stat, Yelp_data = request(API_HOST, SEARCH_PATH, API_KEY, url_params=url_params)
            if stat!=200:
                print('Not 200 Status Code:', stat)
                print(Yelp_data)
                print('sleeping 5 minutes...')
                time.sleep(300)

                if Yelp_data['error']['code']== 'INTERNAL_ERROR':
                    print('retry...')
                    self.scrape_rings(self.rings, self.start_location)
                else:
                    stat, Yelp_data = request(API_HOST, SEARCH_PATH, API_KEY, url_params=url_params)
                    print(stat,'\n',Yelp_data)
                
                exit()

            print(Yelp_data['region'])
            time.sleep(6)
            for business in Yelp_data['businesses']:
                self.business_dict[business['id']] = business
        
        self.loc_list.append([max_businesses, latitude, longitude])
        
        pass

    def previously_pulled(self, lat, long):
        X = np.array(self.loc_list)
        X_tuple = [(x[1], x[2]) for x in X]
        return (lat, long) in X_tuple

    def scrape_rings(self, rings, start_location, radius=3225):
        '''
        Doc Strings:
        INPUT:
        rings:  int for the number to expand out by the jump attribute.
        start_location:  tuple of the latitude, longitude.
        OUTPUT: updates files loging the history of scraping data.
        '''
        point_count = 0
        ring_max = self.ring + int(rings)
        start_time = datetime.datetime.now()
        self.start_location = start_location
        self.rings = rings

        for r in range(self.ring, ring_max):
            self.points += 2

            x = start_location[0]-((self.points/2)*self.jump)
            y = start_location[1]+((self.points/2)*self.jump)
            
            # North
            for n in range(self.points):
                if self.previously_pulled(x,y)==False:
                    self.yelp_business_ring(x, y, radius)
                plt.plot(x,y,marker='o')
                x += self.jump

            point_count += n
            print('North Complete.  Elapsed Time: ', datetime.datetime.now()-start_time, '.  Get ring:', r, ' Points:', point_count)

            # East
            for n in range(self.points):
                if self.previously_pulled(x,y)==False:
                    self.yelp_business_ring(x, y, radius)
                plt.plot(x,y,marker='o')
                y -= self.jump
                
            point_count += n
            print('East Complete.  Elapsed Time: ', datetime.datetime.now()-start_time, '.  Get ring:', r, ' Points:', point_count)

            # South
            for n in range(self.points):
                if self.previously_pulled(x,y)==False:
                    self.yelp_business_ring(x, y, radius)
                plt.plot(x,y,marker='o')
                x -= self.jump

            point_count += n
            print('South Complete.  Elapsed Time: ', datetime.datetime.now()-start_time, '.  Get ring:', r, ' Points:', point_count)

            # West
            for n in range(self.points):
                if self.previously_pulled(x,y)==False:
                    self.yelp_business_ring(x, y, radius)
                plt.plot(x,y,marker='o')
                y += self.jump

            point_count += n
            print('West Complete.  Elapsed Time: ', datetime.datetime.now()-start_time, '.  Get ring:', r, ' Points:', point_count)

            self.ring += 1
            self.save_progress()
            
            with open('data/yelp_businesses.pickle', 'wb') as pickleWriter:
                pickle.dump(self.business_dict, pickleWriter, protocol=2)
            
            X = np.array(self.loc_list)
            np.savetxt('data/loc_list.txt', X)
        
        #plt.title('Rings of latitude and Longitude Locations Scrapped')
        #plt.show()

        print('duration:', datetime.datetime.now()-start_time)
        print('start time:', start_time)
        print('end time:', datetime.datetime.now())