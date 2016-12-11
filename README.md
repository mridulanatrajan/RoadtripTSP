Install the following:

1) install django:
sudo apt-get django

2) install gurobipy:
conda install gurobipy

3) obtain a license from the gurobi website and activate it using:
grbgetkey <license>

4) googlemaps API installation:
pip install -U googlemaps


Running the code:

1) make sure the current directory is set to RoadtripTSP

2) To start the server enter the following command:
python manage.py runserver

3) access the following URL: 
127.0.0.1:8000/Salesmen

4) python code for subtour and simulated annealing:views.py
frontend code:templates/tsp.html

References:
CSS template: http://www.w3schools.com/css/
googlemaps API: https://github.com/googlemaps/google-maps-services-python