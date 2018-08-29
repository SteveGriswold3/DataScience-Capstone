from collections import Counter
import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
#from model import 
from flask import Flask, request, render_template, url_for
from pymongo import MongoClient
from bson import json_util

import requests

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')

app.config["APPLICATION_ROOT"] = "/abc/123"

_sequence_number = 0
from html.parser import HTMLParser

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
    return app.send_static_file('business_search.html')

@app.route('/business_search_qry', methods=['POST'])
def submission_business_search():
    state = request.form['state']
    businesses = client.yelp.businesses.find({'state': state}).limit(10)

    return render_template('business.html', businesses=businesses) #json_util.dumps(businesses)

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
    app.run(host='0.0.0.0', port=8083, debug=True)
    
