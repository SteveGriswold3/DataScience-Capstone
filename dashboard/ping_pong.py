from collections import Counter
import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
#from model import 
from flask import Flask, request, render_template, url_for
from pymongo import MongoClient
from bson import json_util

import requests
client = MongoClient()

app = Flask(__name__)

app.config["APPLICATION_ROOT"] = "/abc/123"

_sequence_number = 0
from html.parser import HTMLParser

# Functions

def get_city_list():    
    # Old code for complete business list
    #city_list = client.yelp.businesses.aggregate([{'$group': {'_id': {'city': '$city', 'state': '$state'}, 'count': {'$sum':1} } }])
    #city_count = [[city['_id']['city'], city['_id']['state'], city['count']] for city in city_list ]
    
    # New code only pull businesses with reviews rated
    reviews = client.yelp.reviews.find({'cluster': {'$exists': True}}, {'_id': False, 'bus_id': True})
    bus_stats = set()
    for review in reviews:
        bus_stats.add(review['bus_id'])

    city_summary_data = client.yelp.businesses.find({}, {'_id': False, 'id': True, 'state': True, 'city': True, 'rating': True, } )
    #city_list = [[bus['city'], bus['state'], bus['rating']] for bus in city_summary_data if bus['id'] in bus_stats]
    city_list = [bus['city'] for bus in city_summary_data if bus['id'] in bus_stats]
    cities = set(city_list)
    
    return sorted(cities)


def find_business_data(kwargs):
    print(kwargs)
    return bdb.find(kwargs, {'_id': False, 'url': True, 'id': True, 'cluster': True, 'prob': True, 'name': True, 'review_count': True, 'rating': True, 'latitude': True, 'longitude': True, 'price': True })

def business_search_params(state='AZ', city='Phoenix', prob='None', lat=None, long=None):
    bus = {}
    bus['price'] = {'$exists': True}
    if lat!=None and long!=None:
        bus['$and'] = [{ 'latitude': { '$lt': (lat+0.2)}}, 
                        { 'latitude': { '$gt': (lat-0.2)}},
                        { 'longitude': { '$lt': (long+0.2) }}, 
                        { 'longitude': { '$gt': (long-0.2) }}]
    else: 
        bus['state'] = state
        if city != 'None':
            bus['city'] = city
    
    if prob!='None':
        prob=float(prob)
        if '$and' in bus.keys():
            bus['$and'].append({'prob': { '$lt': (prob+0.40)}})
            bus['$and'].append({ 'prob': { '$gt': (prob-0.40)}})
        else:
            bus['$and'] = [{ 'prob': { '$lt': (prob+0.40)}}, 
                            { 'prob': { '$gt': (prob-0.40)}}]
    
    return find_business_data(bus)

# Server Class
class score_board(object):
    def __init__(self):
        
        pass

    def import_data(self, filename):
        self.match_list = pd.read_csv(filename, delimiter='\t')
        pass

    def save_data(self):
        
        pass

# Form page to submit text
@app.route('/')
def submission_ping_pong():
    
    return '''
        <form action="/ping_pong_update" method='POST' >
            <h1>Ping Pong</h1>
            <div>
                <div>
                    <div>Date:</div>
                    <input type="text" name="date" />
                    
                    <div>Player:</div>
                    <input type="text" name="player" />

                    <div>Game:</div>
                    <input type="text" name="game" />

                    <div>Singles:</div>
                    <input type="text" name="singles" />

                    <div>Score:</div>
                    <input type="text" name="score" />
                    
                    <div>Opponent:</div>
                    <input type="text" name="opponent" />
                    <br>
                    <br>
                <input type="submit" />
            </div>
        </form>
        '''

@app.route('/state_summary')
def state_summary():
    state_summary_data = client.yelp.businesses.aggregate([{'$group':{'_id':'$state', 'rating': {'$avg': '$rating'}, 'count': {'$sum':1} } }, {'$sort': { 'count': -1} }, {'$match': {'count': {'$gte': 100} } } ] )
    return render_template('state_summary.html', state_summary_data=state_summary_data)

@app.route('/state_count.json')
def state_count_json():
    state_count = client.yelp.businesses.aggregate([{'$group':{'_id':'$state', 'count': {'$sum':1} } }, {'$sort': { 'count': -1} }, {'$match': {'count': {'$gte': 100} } }, {'$limit': 6 } ] )
    return json_util.dumps(state_count, ensure_ascii=False)

@app.route('/business_search')
def to_business_search():
    return render_template('business_search.html', city_list=zip(np.arange(0,len(city_list),1), city_list))

@app.route('/business_search_qry', methods=['POST'])
def submission_business_search():
    print('Business Search Query')
    
    city = request.form['city']
    #decode city
    city = int(city)
    city = [c for idx, c in zip(np.arange(0,len(city_list),1), city_list) if idx==city]
    city = city[0]

    state = request.form['state']
    prob = request.form['sentiment']
    cat = request.form['category']
    
    reviews = rdb.find({'cluster': {'$exists': True}}, {'_id': False, 'bus_id': True, 'cluster': True, 'sentiment': True })
    
    #state='AZ', city='Phoenix', prob=None, lat=None, long=None
    businesses = business_search_params(state=state, city=city, prob=prob)
    bus_search_ids = [bus['id'] for bus in businesses]
    print(len(bus_search_ids), 'Businesses Queried')
    
    #filter Cat
    if cat=='None':
        reviews = [review for review in reviews if review['bus_id'] in bus_search_ids]
    else:
        reviews = [review for review in reviews if review['bus_id'] in bus_search_ids and review['cluster']==cat]
    print(len(reviews), 'Reviews Found for', len(bus_search_ids), 'Businesses')

    bus_stats = {}
    for review in reviews:
        bus_id = review['bus_id']
        if bus_id not in bus_stats.keys():
            bus_stats[bus_id] = {}
            bus_stats[bus_id]['reviews'] = 1
        else:
            bus_stats[bus_id]['reviews'] += 1
        
        cluster = review['cluster']
        if cluster not in bus_stats[bus_id].keys():
            bus_stats[bus_id][cluster] = 1
        else:
            bus_stats[bus_id][cluster] += 1
        
        sentiment = review['sentiment']
        if sentiment not in bus_stats[bus_id].keys():
            bus_stats[bus_id][sentiment] = 1
        else:
            bus_stats[bus_id][sentiment] += 1

    print(len(bus_stats), 'Businesses Found for Category', len(bus_search_ids), 'Businesses')

    df = pd.DataFrame.from_dict(bus_stats)
    df.fillna(0, inplace=True)

    X = np.array(df.values)
    X = X.transpose()

    y=np.zeros((len(X)))

    knn = KNeighborsClassifier(n_neighbors=4,n_jobs=4)
    knn.fit(X, y)
    if len(X)<5:
        rec_index = knn.kneighbors([X[np.random.randint(len(X),size=1)[0],:]], len(X), return_distance=False)
    else:
        rec_index = knn.kneighbors([X[np.random.randint(len(X),size=1)[0],:]], 5, return_distance=False)

    recommended_businesses = [b for idx, b in enumerate(df.columns) if idx in rec_index]
    print(recommended_businesses)

    businesses = business_search_params(state=state, city=city, prob=prob)
    
    search_results = []
    for bus in businesses:
        print(bus)
        if bus['id'] in recommended_businesses:
            print('Test: True')
            search_results.append({'id': bus['id'],
            'name': bus['name'],
            'review_count': bus['review_count'],
            'rating': bus['rating'],
            'latitude': bus['latitude'],
            'longitude': bus['longitude'],
            'price': bus['price']})

    return render_template('businesses.html', businesses=search_results) #json_util.dumps(businesses)

@app.route('/business', methods=['POST'])
def business_details():
    print('Business Detail')
    
    business_id = request.form['bus']    
    print(business_id.rstrip('/'))

    business_data = client.yelp.businesses.find({'id': business_id.rstrip('/')})
    #for x in business_data:
     
    businesses = business_search_params(lat = business_data[0]['latitude'], long = business_data[0]['longitude'], prob=business_data[0]['prob'])
    bus_search_ids = [bus['id'] for bus in businesses]
    print(len(bus_search_ids), 'Businesses Queried')
    
    reviews = rdb.find({'cluster': {'$exists': True}}, {'_id': False, 'bus_id': True, 'cluster': True, 'sentiment': True })
    reviews = [review for review in reviews if review['bus_id'] in bus_search_ids]
    
    print(len(reviews), 'Reviews Found for', len(bus_search_ids), 'Businesses')

    bus_stats = {}
    for review in reviews:
        bus_id = review['bus_id']
        if bus_id not in bus_stats.keys():
            bus_stats[bus_id] = {}
            bus_stats[bus_id]['reviews'] = 1
        else:
            bus_stats[bus_id]['reviews'] += 1
        
        cluster = review['cluster']
        if cluster not in bus_stats[bus_id].keys():
            bus_stats[bus_id][cluster] = 1
        else:
            bus_stats[bus_id][cluster] += 1
        
        sentiment = review['sentiment']
        if sentiment not in bus_stats[bus_id].keys():
            bus_stats[bus_id][sentiment] = 1
        else:
            bus_stats[bus_id][sentiment] += 1

    print(len(bus_stats), 'Businesses Found for Category', len(bus_search_ids), 'Businesses')

    df = pd.DataFrame.from_dict(bus_stats)
    df.fillna(0, inplace=True)

    X = np.array(df.values)
    X = X.transpose()

    y=np.zeros((len(X)))

    knn = KNeighborsClassifier(n_neighbors=4,n_jobs=4)
    knn.fit(X, y)
    if len(X)<5:
        rec_index = knn.kneighbors([X[np.random.randint(len(X),size=1)[0],:]], len(X), return_distance=False)
    else:
        rec_index = knn.kneighbors([X[np.random.randint(len(X),size=1)[0],:]], 5, return_distance=False)

    recommended_businesses = [b for idx, b in enumerate(df.columns) if idx in rec_index]
    print(recommended_businesses)

    business_data = client.yelp.businesses.find({'id': business_id.rstrip('/')})
    businesses = business_search_params(lat = business_data[0]['latitude'], long = business_data[0]['longitude'], prob=business_data[0]['prob'])
    
    search_results = []
    for bus in businesses:
        print(bus)
        if bus['id'] in recommended_businesses:
            print('Test: True')
            search_results.append({'url': bus['url'],
            'name': bus['name'],
            'review_count': bus['review_count'],
            'rating': str(round(float(bus['rating']),0)),
            'latitude': bus['latitude'],
            'longitude': bus['longitude'],
            'price': bus['price']})

    return render_template('business.html', business_detail=business_data, businesses=search_results)

@app.route('/ping_pong_update', methods=['POST'] )
def ping_pong_update():
    #get form inputs
    date = request.form['date']
    player = request.form['player']
    game = request.form['game']
    singles = request.form['singles']
    score = request.form['score']
    opponent = request.form['opponent']

    #update data
    match_list = pd.read_csv('../data/ping_pong.txt', delimiter='\t')
    match_list.loc[len(match_list['date'])] = [date, player, game, singles, score, opponent]
    match_list.to_csv('../data/ping_pong.txt', sep='\t', index=False)

    return render_template('ping_pong.html', data=zip(match_list['date'].values, match_list['name'].values, match_list['game'].values, match_list['single'].values, match_list['player'].values, match_list['opponent'].values))    

@app.route('/ping_pong')
def to_ping_pong():
    match_list = pd.read_csv('../data/ping_pong.txt', delimiter='\t')
    return render_template('ping_pong.html', data=zip(match_list['date'].values, match_list['name'].values, match_list['game'].values, match_list['single'].values, match_list['player'].values, match_list['opponent'].values))    

@app.route('/index')
def to_index():
    tasks = pd.read_csv('../data/agile_tasks.txt')
    cold = tasks[tasks['status']=='Not Checked Out']['status'].count()
    out = tasks[tasks['status']=='Checked Out']['status'].count()
    complete = tasks[tasks['status']=='Complete']['status'].count()
    return render_template('index.html', agile_data=tasks.values, cold=cold, out=out, complete=complete )

@app.route('/update_tasks', methods=['POST'])
def update_agile_task():
    sl = request.form['swim_lane']
    tsk = request.form['task']
    new_status = request.form['agile_status']
    print(sl, tsk, new_status)

    # import data
    tasks = pd.read_csv('../data/agile_tasks.txt')

    # update data
    val = tasks[tasks['swim_lane']==sl][tasks['task']==tsk]['status'].index
    print(val)
    #tasks.set_value(val[0], 'status', new_status)
    #tasks.to_csv('../data/agile_tasks.txt', index=False)

    cold = tasks[tasks['status']=='Not Checked Out']['status'].count()
    out = tasks[tasks['status']=='Checked Out']['status'].count()
    complete = tasks[tasks['status']=='Complete']['status'].count()
    return render_template('index.html', agile_data=tasks.values, cold=cold, out=out, complete=complete )

@app.route('/donate')
def to_donate():
    return app.send_static_file('donate.html')
    
if __name__ == '__main__':
    city_list = get_city_list()

    client = MongoClient()
    db = client.yelp
    bdb = db.businesses
    rdb = db.reviews

    reviews = rdb.find({'cluster': {'$exists': True}}, {'_id': False, 'bus_id': True, 'cluster': True, 'sentiment': True })

    app.run(host='0.0.0.0', port=8083, debug=True)
    
