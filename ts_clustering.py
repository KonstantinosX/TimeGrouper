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
# from matplotlib import pyplot as plt
from math import floor
import math
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

    def trimZeros(self):
        # print type(self.val)
        # print self.val
        for i in range(len(self.val) -1, -1, -1):
            if self.val[i] != 0.0:
                # self.val = self.val[:i]
                # print self.val[:i+1]
                if i >0:
                    return self.val[:i+1]
                else:
                    return self.val

def JSONifyData(data):
    json = []
    for ts in data:
        json.append({'name': ts.ptchNm , 'app': ts.appNm, 'updateMech': ts.upM, 'exploitable': ts.expFlag})
    return json

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
        self.slctDataMat = None
        self.slctNum = 0
        self.slctApp = {'all'}
        self.slctUM = {'all'}
        self.slctExpF = {'all'}
        #similarity matrix and clustering result based on selected data
        self.simMat = None
        self.cluster = None
        #summary of similarity matrix, every smmSc*smmSc integrated into one value
        self.simMatSmm = None
        self.smmSc = 1
        #data ordered after clustering
        self.clstData = []
        self.clstSimMat = None #this is the final matrix we should use
        self.clstLbl = [] #indicate the cluster ID of each data in clustData
        self.clstNum = 0 #number of clusters
        #the patch name of TS in similarity matrix
        self.patchOrdering = None
        self.summaryOrdering = None

        #generalized filters
        self.filters = {}


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

    #generalized filters
    def setFilter(self,filterName,filterValue):
        self.filters[filterName] = filterValue

    def slctGeneralTSData(self):
        self.slctData = db.getall()
        for filt, values in ts.iteritems():
            self.slctData = [ts for ts in self.slctData if ts[filt] in values]
            #Requires testing and integration

    def slctTSData(self):
        self.slctData = self.tsData
        #filter by application
        if not 'all' in self.slctApp:
            self.slctData = [ts for ts in self.slctData if ts.appNm in self.slctApp]
        if not 'all' in self.slctUM:
            self.slctData = [ts for ts in self.slctData if ts.upM in self.slctUM]
        if not 'all' in self.slctExpF:
            # print self.slctExpF
            self.slctData = [ts for ts in self.slctData if ts.expFlag in self.slctExpF]
        print 'selected data:', len(self.slctData)

    def getSimMat(self, type = 'euclidean', ftr_type = 'data', orderFlag = True, pca_dim=20):
        if ftr_type == 'ftr':
            #use input features
            self.slctData = [ts for ts in self.slctData if ((ts.ftr is not None) and (len(ts.ftr) > 0))]
            dataMat = [ts.ftr for ts in self.slctData]
        elif ftr_type == 'data':
            #use input data
            dataMat = [ts.val for ts in self.slctData]
        else:
            print 'unknown ftr_type for ftr_type:', ftr_type
        if pca_dim > len(dataMat):
            pca_dim = int(math.ceil(len(dataMat)/2.0))

        if type  == 'euclidean': #euclidean distance based on time series data
            self.simMat = skmpw.euclidean_distances(dataMat)
        elif type == 'pca_euc': #extract feature based on PCA, then use Euclidean distance
            pca = skd.PCA(n_components=pca_dim)
            dataMat = pca.fit_transform(dataMat)
            self.simMat = skmpw.euclidean_distances(dataMat)
        elif type == 'nmf_euc': #extract feature based on NMF, then use Euclidean distance
            nmf = skd.NMF(n_components=pca_dim)
            dataMat = nmf.fit_transform(dataMat)
            self.simMat = skmpw.euclidean_distances(dataMat)
        elif type =='ica_euc': #extract feature based on ICA, then use Euclidean distance
            ica = skd.FastICA(n_components=pca_dim)
            dataMat = ica.fit_transform(dataMat)
            self.simMat = skmpw.euclidean_distances(dataMat)
        elif type =='cosine':
            self.simMat = skmpw.pairwise_distances(dataMat, metric='cosine')
        elif type == 'pca_cos': #extract feature based on PCA, then use cosine distance
            pca = skd.PCA(n_components=pca_dim)
            dataMat = pca.fit_transform(dataMat)
            self.simMat = skmpw.pairwise_distances(dataMat, metric='cosine')
        elif type == 'nmf_cos': #extract feature based on NMF, then use cosine distance
            nmf = skd.NMF(n_components=pca_dim)
            dataMat = nmf.fit_transform(dataMat)
            self.simMat = skmpw.pairwise_distances(dataMat, metric='cosine')
        elif type =='ica_cos': #extract feature based on ICA, then use cosine distance
            ica = skd.FastICA(n_components=pca_dim)
            dataMat = ica.fit_transform(dataMat)
            self.simMat = skmpw.pairwise_distances(dataMat, metric='cosine')
        else:
            print 'unknown type for similarity matrix: ', type

        #rearrange the order of data in simMat
        self.slctDataMat = dataMat
        if orderFlag:
            link = spc.hierarchy.linkage(self.simMat)
            dend = spc.hierarchy.dendrogram(link, no_plot=True)
            order = dend['leaves']
            self.slctData = [self.slctData[i] for i in order] #rearrange order
            self.simMat = [self.simMat[i] for i in order]
            for i in xrange(len(self.simMat)):
                self.simMat[i] = [self.simMat[i][j] for j in order]
            self.slctDataMat = [self.slctDataMat[i] for i in order]
        # self.patchOrdering = [ts.ptchNm for ts in self.slctData] #record new ordering
        self.patchOrdering = JSONifyData(self.slctData) # Deok wants all the data for each patch in the response
        self.clstData = self.slctData
        self.clstSimMat = self.simMat


    def getSimMatSummary(self, maxSize):
        ttlSz = len(self.clstSimMat)
        sc = 2.0
        while ttlSz/sc > maxSize:
            sc = 2.0*sc
        print "Summarizing by factor of :"+ str(sc)
        newSz = int(math.floor(ttlSz/sc))
        sc = int(sc)
        simMat = []
        summaryOrdering = []
        groupSum = []
        counter = 0
        for i in xrange(newSz):
            simMat.append([])
            for j in xrange(newSz):
                ttl = 0
                for i2 in xrange(sc):
                    for j2 in xrange(sc):
                        ttl += self.simMat[i*sc+i2][j*sc+j2]
                    nm_i = self.patchOrdering[i*sc+i2]['name']
                        # nm_j = self.patchOrdering[j*sc+j2]['name']
                        # tile = []
                        # tile.append(nm_i)
                        # tile.append(nm_j)
                        # groupSum.append(tile)
                    if nm_i not in groupSum:
                        groupSum.append(nm_i)
                        # if nm_j not in groupSum:
                        #     groupSum.append(nm_j)

                simMat[i].append(ttl)
                # generate ordering of apps for summary matrix.
            summaryOrdering.append({'name': 'group'+str(counter), 'patches': groupSum})
            groupSum = []
            counter = counter + 1
        self.simMatSmm = simMat
        self.smmSc = sc
        # print summaryOrdering
        self.summaryOrdering = summaryOrdering


    def getCluster(self, type = 'kmeans', cNum = 20):
        if cNum > len(self.slctDataMat):
            cNum = int(math.ceil(len(self.slctDataMat)/5.0))
        if type == 'kmeans': #kmeans clustering
            cm = skc.KMeans(cNum)
            self.cluster = cm.fit_predict(np.array(self.slctDataMat))
        elif type == 'ap': #affinity propagation
            cm = skc.AffinityPropagation(affinity='euclidean')
            self.cluster = cm.fit_predict(np.array(self.slctDataMat))
            cNum = len(cm.cluster_centers_indices_)
        elif type == 'meanshift': #means shift
            cm = skc.MeanShift()
            self.cluster = cm.fit_predict(np.array(self.slctDataMat))
            cNum = len(cm.cluster_centers_)
        elif type == 'spectral': #spectral
            cm = skc.SpectralClustering(cNum)
            self.cluster = cm.fit_predict(np.array(self.slctDataMat))
        elif type == 'hc': #hierarchical
            cm = skc.AgglomerativeClustering(cNum)
            self.cluster = cm.fit_predict(np.array(self.slctDataMat))
        elif type == 'dbscan': # DBSCAN
            cm = skc.DBSCAN()
            self.cluster = cm.fit_predict(np.array(self.slctDataMat))
            cNum = len(cm.core_sample_indices_ )
            #print cNum
        else:
            print 'unknown cluster type:', type

        #use clustering result to rearrange the order of
        clst2idx = [[] for i in xrange(cNum)]
        for i in xrange(len(self.cluster)):
            clst2idx[self.cluster[i]].append(i)
        #caculate average to decide order of clusterings
        muClIdx = [np.mean(clst2idx[i]) for i in xrange(cNum)]
        idx = np.argsort(muClIdx)
        order =[]
        for i in xrange(cNum):
            order.extend(np.sort(clst2idx[idx[i]]))
        self.clstData = [self.slctData[i] for i in order]
        self.clstSimMat = [self.simMat[i] for i in order]
        for i in xrange(len(self.clstSimMat)):
            self.clstSimMat[i] = [self.clstSimMat[i][j] for j in order]
        self.clstLbl = [self.cluster[i] for i in order]
        self.clstNum = cNum
        # self.patchOrdering = [self.patchOrdering[i] for i in order]
        self.patchOrdering = JSONifyData(self.clstData)


    def drawSimMat(self):
        plt.figure()
        plt.imshow(self.simMat, interpolation='nearest')
        plt.title('SimMat')
        plt.colorbar()
        plt.ylabel('patches')
        plt.xlabel('patches')

    def drawClstSimMat(self):
        plt.figure()
        plt.imshow(self.clstSimMat, interpolation='nearest')
        plt.title('SimMat')
        plt.colorbar()
        plt.ylabel('patches')
        plt.xlabel('patches')

    def toJSON(self):
        """
        Returns a JSON of the similarity matrix and its metadata (patches and their ordering)

        Format:
        [[ 'patch1', 'patch2', ... ] , [similatiry matrix]]

        If we have a lot of data (number of patches > 100 ) it includes the Summary of the similarity matrix like so:

        Format:
        [[summary matrix] , [ 'patch1', 'patch2', ... ] , [similatiry matrix]]
        """

        jsonToRet = []
        rowJson = []
        matrixJson = []

        if len(self.slctData) > 100:
            self.getSimMatSummary(100)
            jsonToRet.append(self.summaryOrdering)
            for i in range(0,len(self.simMatSmm)):
                for n in self.simMatSmm[i]:
                    rowJson.append(n)
                matrixJson.append(rowJson)
                rowJson = []
            jsonToRet.append(matrixJson)

        jsonToRet.append(self.patchOrdering)
        # jsonToRet = []
        rowJson = []
        matrixJson = []

        for i in range(0,len(self.simMat)):
            for n in self.simMat[i]:
                rowJson.append(n)
            matrixJson.append(rowJson)
            rowJson = []
        jsonToRet.append(matrixJson)
        return jsonToRet

    def drawSimMatSummary(self):
        plt.figure()
        labels = [ts.ptchNm for ts in self.slctData]
        plt.imshow(self.simMatSmm, interpolation='nearest')
        plt.title('SimMat')
        plt.colorbar()
        plt.ylabel('patches')
        plt.xlabel('patches')

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
    def printAllAppNm(self):
        for i in xrange(self.tsNum):
            print self.tsData[i].appNm
