'''
This flask RESTful app is part of
TimeGrouper, our CMSC734 Term Project

@author: Konstantinos Xirogiannopoulos, kostasx@cs.umd.edu, 4/19/2015
'''

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from flask.ext.cors import CORS, cross_origin
from ts_clustering import TSCluster
from StringIO import StringIO
import json
import pickledb
import os

# Initial assignments
main = Flask(__name__)
api = Api(main)
cors = CORS(main)

currentData = pickledb.load('currData.db',False) #open db
db = pickledb.load('database.db',False)
dataPath = os.path.dirname(os.path.abspath('__file__'))
# currData = TSCluster()
simMatParser = reqparse.RequestParser()
patchesParser = reqparse.RequestParser()

patchesParser.add_argument('patchId', type=str, action='append')
patchesParser.add_argument('highlight', type=str, action='append')
simMatParser.add_argument('appName', type=str, action='append')
simMatParser.add_argument('updateMech', type=str, action='append')
simMatParser.add_argument('exploitable', type=str, action='append')
simMatParser.add_argument('simMetric', type=str, required=True)
simMatParser.add_argument('cAlgorithm', type=str, required=True) #clustering algorithm

@main.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

def loadData(simMetric, cAlgorithm, app_filter=['all'],um_filter=['all'],exp_filter=['all']):
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
    if(app_filter != None):
        tsc.setAppFilter(app_filter)
    if(um_filter != None):
        tsc.setUMFilter(um_filter)
    if(exp_filter != None):
        for f in exp_filter:
            if f.lower() == 'true':
                exp_filter = [True]
            else:
                exp_filter = [None]
        tsc.setExpFilter(exp_filter)
    tsc.slctTSData()
    # print simMetric
    tsc.getSimMat(type=simMetric, ftr_type = 'data', orderFlag = True)
    tsc.getCluster(type=cAlgorithm)
    currentData.set('currData',tsc)
    currData = tsc
    return tsc
    # return tsc.toJSON()

def abort_if_patch_doesnt_exist(patch_id):
    """
    Aborts and returns an appropriate message if the patches requested don't exist
    """
    currData = currentData.get('currData')
    if patch_id not in  currData.ptchnm2idx:
        abort(404, message="Patch {} doesn't exist".format(patch_id))

def gethighlights(highlight,appNSplits):
    toRet = []
    for colIdx, col in enumerate(appNSplits):
        if col in highlight:
            for rowIdx, row in enumerate(appNSplits):
                if row in highlight:
                    toRet.append([colIdx,rowIdx])
    return toRet

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
        args = patchesParser.parse_args()
        patchIds = args['patchId']
        toHighlight = args['highlight']
        appNameSplits = [t.split("_")[0] for t in currData.patchOrdering]
        if toHighlight != None:
            toReturn = gethighlights(toHighlight,appNameSplits)
            return json.dumps(toReturn)
        for a in patchIds:
            abort_if_patch_doesnt_exist(a)
            timeSeriesD = currData.slctData[currData.ptchnm2idx[a]].trimZeros()
            entry = {str(a) : timeSeriesD}
            toReturn.append(entry)
        jsonToRet = json.dumps(toReturn)
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
        args = simMatParser.parse_args()
        appNames = args['appName']
        updateMech = args['updateMech']
        exploitable = args['exploitable']
        simMetric = args['simMetric']
        clusteringAlg = args['cAlgorithm']
        return loadData(simMetric,clusteringAlg,appNames,updateMech,exploitable).toJSON()
        # return None


# The endpoints to the API. To access it http://127.0.0.1:5000/<endpoint>
api.add_resource(SMatrix, '/getSimMatrix', '/getSimMatrix/<app_filter>')
api.add_resource(PatchTS, '/getPatches', '/getPatches/<patch_id>')

if __name__ == '__main__':
    main.run(debug=True)
