echo "After ssh dsi is running"
echo "script copies files to use"

scp ../.gitignore/yelp_api_key.yaml macdevro:yelp_api_key.yaml
scp ../data/yelp_businesses.pickle macdevro:yelp_businesses.pickle

scp server_setup.sh macdevro:src/server_setup.sh

echo "done moving files"

echo "go to the server and run sh server_setup.sh"
echo -n "Press Enter when ssh server is ready!"
read answer

echo "Thanks"

echo "Now moving flask app files"
scp -r dashboard/static/ macdevro:flaskapp/static/
scp -r dashboard/templates/ macdevro:flaskapp/templates/

echo "Now moving data"
scp -r data/ macdevro: