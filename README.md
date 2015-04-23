# TimeGrouper
To run the TimeGrouper backend __localy__ in a python virtual environment, follow these steps:

1. Run ```./setup.sh``` on Linux/Mac and ```setup.bat``` on Windows. This will install all python packages needed in a virtual environment in  ```flask/```

2. Activate the virtual environment ```source flask/bin/activate```

3. Run ```python app.py```

The RESTful service should now be running at: http://localhost:5000/

Service Endpoints:
- GET: http://localhost:5000/getSimMatrix/{_appname_}

- POST: http://localhost:5000/getSimMatrix  -- (__Note__: If #patches > 100 the _summary_ of the similarity matrix is included in the response as the first json array.)

 1. with {simMetric : 'some-similarity-Metric', cAlgorithm : 'clustering-algorithm'} these are __required__  
 2. with {filter : 'chrome' , filter : 'firefox' ...etc} in the request to filter by _app name_  
 3. with {updateMech : 'SU', updateMech : 'PD' ...} to filter by _update mechanism_  
 5. {exploitable='true'} to filter by _verified exploitability_ (true if patch has been exploited in the past)

- GET:  http://localhost:5000/getPatches/{_patch_id_}

- POST:
http://localhost:5000/getPatches
 1. with {patchId : 'chrome_001' , patchId : 'firefox_003' ...etc} in the request
 2. with {highlight : 'chrome', updateMech : 'firefox' ...} to highlight by _app name_ (highlights the similarity matrix positions that correspond to a similarity for two patches that _both_ fit the highlighting condition). Returns [i,j] pairs for the boxes that should be highlighted  
