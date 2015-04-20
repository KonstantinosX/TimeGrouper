# TimeGrouper
To run the TimeGrouper backend in a python virtual environment, follow these steps:

1. Run ```./setup.sh``` on Linux/Mac and ```setup.bat``` on Windows. This will install all python packages needed in a virtual environment in  ```flask/```

2. Activate the virtual environment ```source flask/bin/activate```

3. Run ```python app.py```

The RESTful service should now be running at: http://localhost:5000/

Service Endpoints:
- GET: http://localhost:5000/getSimMatrix/{_appname_}

- POST: http://localhost:5000/getSimMatrix  
with {filter : 'chrome' , filter : 'firefox' ...etc} in the request

- GET:  http://localhost:5000/getPatches/{_patch_id_}

- POST:
http://localhost:5000/getPatches
with {patchId : 'chrome_001' , patchId : 'firefox_003' ...etc} in the request
