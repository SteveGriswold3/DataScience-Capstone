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
sudo pip3 install pymongo

echo 'making directories' 
mkdir ~/src
mkdir ~/data