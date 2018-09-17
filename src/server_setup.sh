echo 'Setting up Packages'

sudo apt-get update
sudo apt-get -y install python3-pip

sudo pip3 install pandas
sudo pip3 install numpy

sudo -H pip3 install jupyter
python3 -m pip install ipykernel
sudo pip3 install beautifulsoup4

sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi
sudo pip3 install flask

mkdir ~/flaskapp
sudo ln -sT ~/flaskapp /var/www/html/flaskapp

sudo pip3 install -U scikit-learn
sudo pip3 install scipy

sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo service mongod start

sudo pip3 install pymongo

echo 'making directories' 
mkdir ~/src
mkdir ~/data