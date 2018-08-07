# DataScience-Capstone
Repository for Galvanize Data Science Immersive Capstone Project.

## Project Overview:  Yelp Review Predictor

Pulling the Yelp Review comments via the Yelp API.  Extract training data for using natural language processing to train a model.  The model will predict based on the words used in the training reviews, which words correlate to a specific review.

If time allows in the capstone, the concept could be expanded to segment the businesses based on words used by customers review.  The classification could be used to create a recommendation for users based on a business search.  To recommend similar restaurants in the area.

## Tools and Resources:
    Yelp API
    Python
    Spark SQL
    AWS - EC2, S3
    MongoDB
    Flask
    HTML5

##Data Workflow:
    Yelp API Scrapping
        Business Search
        Review Search
        Spark DataFrame
        Write Parquet to S3

    Model Fitting
        Open Parquet with Spark SQL
        Convert to Dict into MongoDB on EC2
        Flask App for queries of the App Data
            Queries (HTML Templates)
                Proximities Counts
                nearest neighbors
                Customer Review Averages
                Natual Language Processing w/ word cloud
                    Star - Word Frequency
                    Classify Restaurants - Kmeans


    Prediction Collection
        Store data on Prediction results
        Store request features (X, predict)

## 1. Phase 1
    a. Web Scrapping
        Python
        

##Future State
If the app was productionalized, then the user request could trigger the data analysis and model fitting to return a prediction for the area the user is located.


