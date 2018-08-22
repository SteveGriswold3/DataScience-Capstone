echo "After ssh dsi is running"
echo "script copies files to use"

scp ../.gitignore/yelp_api_key.yaml dsi:yelp_api_key.yaml
scp ../data/yelp_businesses.pickle dsi:yelp_businesses.pickle
