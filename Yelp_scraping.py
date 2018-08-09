#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 13:21:45 2018

@author: Steve Griswold

"""

from timeit import Timer
from yelp_helpers import request
from yelp_helpers import load_api_key
import pandas as pd
import pickle
import numpy as np
import datetime
import matplotlib.pyplot as plt

key = load_api_key()
API_KEY = key['client_secret']
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'

class Yelp_Scrapper:
    def __init__(self, ):
        '''
        Doc Strings:

        ring: Ring count from main latitude and longitude point.

        points: number of locations in the in the loop

        '''
        with open("scrappingProgress.txt", "r") as f:
            self.ring = f.readline()
            self.points = f.readline()
            self.jump = f.readline()

        loc_list = np.loadtxt('loc_list.txt')
        self.loc_list = [x for x in loc_list]

        with open('yelp_businesses.pickle', 'rb') as pickleReader:
            business_dict = pickle.load(pickleReader)

        pass
        
    def yelp_business_ring(loc_list, bus_dict, longitude, latitude, radius=3225):
        # radius max 12874,     
        url_params = {
                'latitude': latitude,
                'longitude': longitude,
                'radius': radius,
                'limit': 50
            }

        Yelp_data = request(API_HOST, SEARCH_PATH, API_KEY, url_params=url_params)
        for business in Yelp_data['businesses']:
            bus_dict[business['id']] = business
            
        time.sleep(5)

        max_businesses = Yelp_data['total']
        print('Location business count: ', max_businesses)
        offset = 0
        while (offset < max_businesses) and (offset < 1000):
            offset += 50
            url_params = {
                    'latitude': latitude,
                    'longitude': longitude,
                    'radius': radius,
                    'limit': 50,
                    'offset': offset
                }
            
            Yelp_data = request(API_HOST, SEARCH_PATH, API_KEY, url_params=url_params)
            time.sleep(5)
            for business in Yelp_data['businesses']:
                bus_dict[business['id']] = business
        
        loc_list.append([max_businesses, longitude, longitude])
        return bus_dict

    def get_progress():
        with open("scrappingProgress.txt", "r") as f:
            ring = f.readline().rstrip("\n")
            points = f.readline().rstrip("\n")
            jump = f.readline().rstrip("\n")
        
        return int(ring), int(points), float(jump)

    def save_progress(ring, points, jump):
        with open("scrappingProgress.txt", "w") as f:
            f.write(str(ring)+'\n')
            f.write(str(points)+'\n')
            f.write(str(jump)+'\n')

    