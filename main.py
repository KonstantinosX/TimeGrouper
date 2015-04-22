'''
This flask RESTful app is part of
TimeGrouper, our CMSC734 Term Project

@author: Konstantinos Xirogiannopoulos, kostasx@cs.umd.edu, 4/19/2015
'''

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from ts_clustering import TSCluster
from StringIO import StringIO
import json
import pickledb
import os

# Initial assignments
main = Flask(__name__)
api = Api(main)
currentData = pickledb.load('currData.db',False) #open db
db = pickledb.load('database.db',False)
dataPath = os.path.dirname(os.path.abspath('__file__'))
# currData = TSCluster()
parser = reqparse.RequestParser()
parser.add_argument('patchId', type=str, action='append')
parser.add_argument('filter', type=str, action='append')


def loadData(app_filter=['all']):
    """
    Calls the clustering code which reads the data into a python object,
    and loads that python object into pickledb to be called and served to the front end. returns the read python object to be converted to JSON and served.
    """
    if(currentData.get('currData') == None):
        tsc = TSCluster()
        tsc.loadTS(dataPath + os.path.abspath("/data/hazard_alg_TP.input"))
        tsc.loadAttr(dataPath + os.path.abspath("/data/stat.csv"))
        tsc.loadFtr(dataPath + os.path.abspath("/data/ziyun_ftr.input"))
        currentData.set('currData',tsc)
    tsc = currentData.get('currData')
    tsc.setAppFilter(app_filter)
    tsc.slctTSData()
    tsc.getSimMat(type='pca_euc', ftr_type = 'data', orderFlag = True)
    currentData.set('currData',tsc)
    currData = tsc
    return tsc
    # return tsc.toJSON()

def abort_if_patch_doesnt_exist(patch_id):
    """
    Aborts and returns an appropriate message if the patches requested don't exist
    """
    currData = currentData.get('currData')
    print currData.ptchnm2idx
    if patch_id not in  currData.ptchnm2idx:
        abort(404, message="Patch {} doesn't exist".format(patch_id))

class PatchTS(Resource):
    """
    Resource that returns the time series data for all the patches in the request. The request can either contain a single patch (GET) or multiple patches (POST)
    """

    def get(self, patch_id):
        abort_if_patch_doesnt_exist(patch_id)
        return patches[patch_id]

    def post(self):
        currData = currentData.get('currData')
        toReturn = []
        args = parser.parse_args()
        tehArgs = args['patchId']
        print tehArgs
        for a in tehArgs:
            print a
            abort_if_patch_doesnt_exist(a)
            timeSeriesD = currData.tsData[currData.ptchnm2idx[a]].val
            entry = {str(a) : timeSeriesD}
            toReturn.append(entry)
        jsonToRet = json.dumps(toReturn)
        print jsonToRet
        return jsonToRet


#
class SMatrix(Resource):
    """
    Calling a GET on getSimMatrix will load the data into the append
    We assume that this will be the first thing that happens in the app
    """

    def get(self,app_filter='all'):
        matrix = db.get(app_filter)
        if(matrix != None):
            return matrix
        filt = []
        filt.append(app_filter)
        simMatJSON = loadData(filt).toJSON()
        db.set(app_filter,simMatJSON)
        db.dump()
        return simMatJSON

    def post(self):
        args = parser.parse_args()
        argz = args['filter']
        print argz
        return loadData(argz).toJSON()
        # return None


# The endpoints to the API. To access it http://127.0.0.1:5000/<endpoint>
api.add_resource(SMatrix, '/getSimMatrix', '/getSimMatrix/<app_filter>')
api.add_resource(PatchTS, '/getPatches', '/getPatches/<patch_id>')

if __name__ == '__main__':
    main.run(debug=True)
