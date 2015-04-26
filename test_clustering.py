import sklearn.metrics.pairwise as skmpw
import sklearn.cluster as skc
import sklearn.decomposition as skd
from enum import Enum
import csv
import numpy as np
import scipy.spatial.distance as spd
import scipy.cluster as spc
from matplotlib import pyplot as plt
from math import floor
import math
import json
from ts_clustering import TSCluster
import os

if __name__ == '__main__':
    # test demo
    fileFolder = os.path.dirname(os.path.abspath('__file__'))
    tsc = TSCluster()
    tsc.loadTS(fileFolder+'/data/hazard_alg_TP.input')
    tsc.loadAttr(fileFolder+'/data/stat.csv')
    tsc.loadFtr(fileFolder+'/data/ziyun_ftr.input')

    #test for similarity matrix
    '''
    tsc.setAppFilter(['chrome', 'firefox'])
    tsc.slctTSData()
    tsc.getSimMat(ftr_type = 'ftr', orderFlag = True)
    tsc.drawSimMat()
    tsc.getSimMatSummary(100)
    tsc.drawSimMatSummary()
    tsc.getSimMatSummary(50)
    tsc.drawSimMatSummary()
    '''


    tsc.setAppFilter(['acroread'])
    '''
    #use input feature: Ziyun's feature
    tsc.slctTSData()
    tsc.getSimMat(ftr_type = 'ftr', orderFlag = False)
    tsc.drawSimMat()
    tsc.getSimMat(ftr_type = 'ftr', orderFlag = True)
    tsc.drawSimMat()

    #use raw time series and Euclidean distance
    tsc.slctTSData()
    tsc.getSimMat(ftr_type = 'data', orderFlag = False)
    tsc.drawSimMat()
    tsc.getSimMat(ftr_type = 'data', orderFlag = True)
    tsc.drawSimMat()

    #use pca feature of time series and Euclidean distance
    tsc.slctTSData()
    tsc.getSimMat(type='pca_euc', ftr_type = 'data', orderFlag = False)
    tsc.drawSimMat()
    tsc.getSimMat(type='pca_euc', ftr_type = 'data', orderFlag = True)
    tsc.drawSimMat()

    #use nmf feature of time series and Euclidean distance
    tsc.slctTSData()
    tsc.getSimMat(type='nmf_euc', ftr_type = 'data', orderFlag = False)
    tsc.drawSimMat()
    tsc.getSimMat(type='nmf_euc', ftr_type = 'data', orderFlag = True)
    tsc.drawSimMat()

    #use ica feature of time series and Euclidean distance
    tsc.slctTSData()
    tsc.getSimMat(type='ica_euc', ftr_type = 'data', orderFlag = False)
    tsc.drawSimMat()
    tsc.getSimMat(type='ica_euc', ftr_type = 'data', orderFlag = True)
    tsc.drawSimMat()

    #use cosine distance
    tsc.slctTSData()
    tsc.getSimMat(type='cosine', ftr_type = 'data', orderFlag = False)
    tsc.drawSimMat()
    tsc.getSimMat(type='cosine', ftr_type = 'data', orderFlag = True)
    tsc.drawSimMat()
    tsc.slctTSData()
    tsc.getSimMat(type='pca_cos', ftr_type = 'data', orderFlag = False)
    tsc.drawSimMat()
    tsc.getSimMat(type='pca_cos', ftr_type = 'data', orderFlag = True)
    tsc.drawSimMat()
    tsc.slctTSData()
    tsc.getSimMat(type='ica_cos', ftr_type = 'data', orderFlag = False)
    tsc.drawSimMat()
    tsc.getSimMat(type='ica_cos', ftr_type = 'data', orderFlag = True)
    tsc.drawSimMat()
    '''
    #test clustering
    tsc.slctTSData()
    # tsc.getSimMat(type='ica_cos', ftr_type = 'data', orderFlag = False)
    # tsc.getCluster(type='dbscan')
    # tsc.drawSimMat()
    # tsc.drawClstSimMat()
    tsc.getSimMat(type='ica_cos', ftr_type = 'data', orderFlag = True)
    tsc.getCluster(type='dbscan')
    # tsc.drawSimMat()
    # tsc.drawClstSimMat()
    tsc.getSimMatSummary(100)
    tsc.drawSimMatSummary()
    #save matrix
    #tsc.writeSimMatCSV(fileFolder+'\PatchName.csv', fileFolder+'\SimMat.csv')
    plt.show()
