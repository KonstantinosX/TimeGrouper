'''
Python code for CMSC 734 term project,
based on sklearn package

1. load time series data
2. create similarity matrix
3. clustering
4. rearrange index in similarity matrix based on clustering results

@author: Zheng Xu, xuzhustc@gmail.com, 2015/4/8
'''

import sklearn.metrics.pairwise as skmpw
import sklearn.cluster as skc
import sklearn.decomposition as skd
from enum import Enum
import csv
import numpy as np
import scipy.spatial.distance as spd
import scipy.cluster as spc
from matplotlib import pyplot as plt
import json

class PatchTS:
    'this class describe the patching time series'
    'members including the dimension (time points), name of patch, name of application, update mechanism, exploitable flag'
    def __init__(self):
        self.dim = 0
        self.ptchNm = None
        self.appNm = None
        self.upM = None
        self.expFlag = None
        self.val = []
        self.ftr = []

    def setPatchNm(self, nm):
        self.ptchNm = nm

    def setVal(self, val):
        self.val = list(val)

    def setAppNm(self, nm):
        self.appNm = nm

    def setUpM(self, um):
        self.upM = um

    def setExpF(self, ef):
        self.expFlag = ef

    def setFtr(self, ftr):
        self.ftr = list(ftr)



class TSCluster:
    ' this class is used to caculate the similarity matrix and do clustering for time series'
    def __init__(self):
        #members related to time series data
        self.tsNum = 0
        self.tsDim = 0
        self.tsData = []
        self.ptchnm2idx = {}
        #the filters used and the data after filtering
        self.slctData = []
        self.slctNum = 0
        self.slctApp = {'all'}
        self.slctUM = {'all'}
        self.slctExpF = {'all'}
        #similarity matrix and clustering result
        self.simMat = None
        self.cluter = None
        self.patchOrdering = None

    def loadTS(self, tsFile):
        #load time series
        with open(tsFile, 'r') as fid:
            lines = fid.readlines()
            #first line is the number of time series
            parts = lines[0].split()
            self.tsNum = int(parts[1])
            #second line is the dimension of time series, i.e., the maximum date of time series
            parts = lines[1].split()
            self.tsDim = int(parts[1])
            #the rest are time series, format: name\t va1, val2, ... valn\n
            for i in xrange(len(lines)-2):
                line = lines[i+2]
                parts = line.split('\t')
                ts = PatchTS()
                ts.setPatchNm(parts[0])
                parts2 = parts[1].strip(' \t\r\n,').split(',')
                if len(parts2) == self.tsDim:
                    ts.setVal([float(x) for x in parts2])
                else:
                    print 'ts dim: ', self.tsDim, 'vs.', len(parts2)
                self.tsData.append(ts)
                self.ptchnm2idx[ts.ptchNm] = i
        if len(self.tsData) == self.tsNum:
            print 'loaded time series:', self.tsNum

    def loadAttr(self, attFile):
        #load attributes such as update mechanism, application name
        with open(attFile, 'rb') as fid:
            cr = csv.reader(fid, delimiter = ',', quotechar = '"')
            ri = 0
            for row in cr:
                ri = ri + 1
                if 1 == ri:
                    continue #head
                idx = self.ptchnm2idx[row[0]]
                ts = self.tsData[idx]
                #print ts.ptchNm, row[0]
                ts.setAppNm(row[1])
                ts.setUpM(row[2])
                ts.setExpF(bool(row[6]))
            print 'patch time series with attribute:', ri

    def loadFtr(self, ftrFile):
        #load user input ftr for time series
        with open(ftrFile, 'r') as fid:
            lines = fid.readlines()
            #first line is the number of time series
            parts = lines[0].split()
            ftrNum = int(parts[1])
            #second line is the dimension of ftr
            parts = lines[1].split()
            ftrDim = int(parts[1])
            #the rest are ftrs, format: name\t va1, val2, ... valn\n
            for i in xrange(len(lines)-2):
                line = lines[i+2]
                parts = line.split('\t')
                parts2 = parts[1].strip(' \t\r\n,').split(',')
                idx = self.ptchnm2idx[parts[0].strip(' "')]
                ts = self.tsData[idx]
                if len(parts2) == ftrDim:
                    ts.setFtr([float(x) for x in parts2])
                else:
                    print 'feature dim: ', ftrDim, 'vs.', len(parts2)

    def setAppFilter(self, app):
        self.slctApp = set(app)
    def setUMFilter(self, um):
        self.slctUM = set(um)
    def setExpFilter(self, exp):
        self.slctExpF = set(exp)

    def slctTSData(self):
        self.slctData = self.tsData
        #filter by application
        if not 'all' in self.slctApp:
            self.slctData = [ts for ts in self.slctData if ts.appNm in self.slctApp]
        if not 'all' in self.slctUM:
            self.slctData = [ts for ts in self.slctData if ts.upM in self.slctUM]
        if not 'all' in self.slctExpF:
            self.slctData = [ts for ts in self.slctData if ts.expFlag in self.slctExpF]
        print 'selected data:', len(self.slctData)

    def getSimMat(self, type = 'euclidean', ftr_type = 'data', orderFlag = True , pca_dim=20):
        if ftr_type == 'ftr':
            #use input features
            self.slctData = [ts for ts in self.slctData if ((ts.ftr is not None) and (len(ts.ftr) > 0))]
            dataMat = [ts.ftr for ts in self.slctData]
        elif ftr_type == 'data':
            #use input data
            dataMat = [ts.val for ts in self.slctData]
        else:
            print 'unknown ftr_type for ftr_type:', ftr_type

        if type  == 'euclidean':
            self.simMat = skmpw.euclidean_distances(dataMat)
        elif type == 'pca_euc':
            pca = skd.PCA(n_components=pca_dim)
            dataMat = pca.fit_transform(dataMat)
            self.simMat = skmpw.euclidean_distances(dataMat)
        elif type == 'nmf_euc':
            nmf = skd.PCA(n_components=pca_dim)
            dataMat = nmf.fit_transform(dataMat)
            self.simMat = skmpw.euclidean_distances(dataMat)
        else:
            print 'unknown type for similarity matrix: ', type
            #print self.simMat
        self.patchOrdering = [ts.ptchNm for ts in self.slctData] #record ordering
        if orderFlag:
            link = spc.hierarchy.linkage(self.simMat)
            dend = spc.hierarchy.dendrogram(link, no_plot=True)
            order = dend['leaves']
            self.slctData = [self.slctData[i] for i in order] #rearrange order
            self.patchOrdering = [ts.ptchNm for ts in self.slctData] #record new ordering
            self.simMat = [self.simMat[i] for i in order]
            for i in xrange(len(self.simMat)):
                self.simMat[i] = [self.simMat[i][j] for j in order]

    def getCluster(self, type = 'kmeans', cNum = 50):
        dataMat = [ts.val for ts in self.slctData]

    def drawSimMat(self):
        plt.figure()
        labels = [ts.ptchNm for ts in self.slctData]
        plt.imshow(self.simMat, interpolation='nearest')
        plt.title('SimMat')
        plt.colorbar()
        plt.ylabel('patches')
        plt.xlabel('patches')

    def toJSON(self):
        """
        Returns a JSON of the similarity matrix and its metadata (patches and their ordering)

        Format:
        [[ 'patch1', 'patch2', ... ] , [similatiry matrix]]
        """
        jsonToRet = []
        jsonToRet.append(self.patchOrdering)
        rowJson = []
        matrixJson = []

        for i in range(0,len(self.simMat)):
            for n in self.simMat[i]:
                rowJson.append(n)
            matrixJson.append(rowJson)
            rowJson = []
        jsonToRet.append(matrixJson)
        return jsonToRet

    def writeSimMatCSV(self, lblNmFile, matFile):
        lblNm = [ts.ptchNm for ts in self.slctData]
        with open(lblNmFile, 'w') as fid:
            for lbl in lblNm:
                fid.write(str(lbl))
                fid.write('\n')
        with open(matFile, 'w') as fid:
            for row in self.simMat:
                for val in row:
                    fid.write(str(val))
                    fid.write(',')
                fid.write('\n')

if __name__ == '__main__':
    # test demo
    # fileFolder = r'D:\UMD\class\2015Spring\cmsc734\termProject'
    fileFolder = '/Users/kostasx/Desktop/TimeGrouper/data'
    tsc = TSCluster()
    tsc.loadTS(fileFolder+'/hazard_alg_TP.input')
    tsc.loadAttr(fileFolder+'/stat.csv')
    tsc.loadFtr(fileFolder+'/ziyun_ftr.input')
    tsc.setAppFilter(['chrome','firefox'])
    tsc.slctTSData()
    # tsc.getSimMat(ftr_type = 'ftr', orderFlag = False)
    # tsc.drawSimMat()
    tsc.getSimMat(ftr_type = 'ftr', orderFlag = True)
    # print tsc.toJSON()
    #tsc.writeSimMatCSV(fileFolder+'\PatchName.csv', fileFolder+'\SimMat.csv')
    tsc.drawSimMat()
    plt.show()
