#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Description

Usage:
    $python dbscan.py -f DATASET.csv -e EPSILON -m minPoitns

    $python dbscan.py -f crater.csv -e 0.8 -m 2
"""
from sklearn.cluster import DBSCAN
import csv
from collections import defaultdict
from optparse import OptionParser
import matplotlib.pyplot as plt

##################
# クラスタリング結果を返すように実装してください
def clustering(feature, eps, minPoints):
    pred = DBSCAN(eps=eps, min_samples=minPoints).fit_predict(feature)
    return pred
##################

def dataFromFile(fname):
        """Function which reads from the file and yields a generator"""
        file_iter = open(fname, 'rU')
        for line in file_iter:
                line = line.strip().rstrip(',')                         # Remove trailing comma
                record = line.split(',')
                yield record
if __name__ == '__main__':

    optparser = OptionParser()
    optparser.add_option('-f', '--inputFile',
                         dest='input',
                         help='filename containing csv',
                         default=None)
    optparser.add_option('-e', '--epsilon',
                         dest='eps',
                         help='threshold for marge step',
                         default=0.8,
                         type='float')
    optparser.add_option('-m', '--minPoints',
                         dest='minPoints',
                         help='minimum number of points for cluster',
                         default=2,
                         type='int')
    (options, args) = optparser.parse_args()
    inFile = None
    if options.input is None:
            inFile = sys.stdin
    elif options.input is not None:
            inFile = dataFromFile(options.input)
    else:
            print('No dataset filename specified, system with exit\n')
            sys.exit('System will exit')
    eps = options.eps
    minPoints = options.minPoints
##################
#    pred は以下のようなリストが期待されます
#    [1,0,0,2,1,0]
#    この場合、要素の一つ目がクラスタ1に、二つ目がクラスタ0に属していることを意味しています
##################
    feature=[]
    for record in inFile:
        feature.append(list(map(float,record)))
    pred = clustering(feature,eps,minPoints)

#plot nodes
    plt.title("dbscan")
    x=[]
    y=[]
    for i in range(len(set(pred))):
        x.append([])
        y.append([])
    for i in range(len(pred)):
        x[pred[i]].append(feature[i][0])
        y[pred[i]].append(feature[i][1])
    color_list=['red','blue','yellow','green','purple','c', 'olivedrab','gray','pink']
    for i in range(len(x)):
        plt.scatter(x[i],y[i],label=i, c=color_list[i])
    plt.legend()
    plt.show()
