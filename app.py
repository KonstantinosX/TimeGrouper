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
app = Flask(__name__)
api = Api(app)
db = pickledb.load('example.db',False) #open db
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

    tsc = TSCluster()
    tsc.loadTS(dataPath + os.path.abspath("/data/hazard_alg_TP.input"))
    tsc.loadAttr(dataPath + os.path.abspath("/data/stat.csv"))
    tsc.loadFtr(dataPath + os.path.abspath("/data/ziyun_ftr.input"))
    tsc.setAppFilter(app_filter)
    tsc.slctTSData()
    tsc.getSimMat(ftr_type = 'ftr', orderFlag = True)
    db.set('currData',tsc)
    currData = tsc
    return tsc
    # return tsc.toJSON()

def abort_if_patch_doesnt_exist(patch_id):
    """
    Aborts and returns an appropriate message if the patches requested don't exist
    """
    currData = db.get('currData')
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
        currData = db.get('currData')
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
        filt = []
        filt.append(app_filter)
        return loadData(filt).toJSON()

    def post(self):
        args = parser.parse_args()
        argz = args['filter']
        print argz
        return loadData(argz).toJSON()
        # return None


# The endpoints to the API. To access it http://127.0.0.1:5000/<endpoint>
api.add_resource(SMatrix, '/getSimMatrix', '/getSimMatrix/<app_filter>')
api.add_resource(PatchTS, '/getPatches')

if __name__ == '__main__':
    app.run(debug=True)
