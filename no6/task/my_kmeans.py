import numpy as np
import random

class KMeams(object):
    def __init__(self,cluster_num):
        self.cluster_num = cluster_num
        # 次元数は入力データの次元数と同じにする必要あり
        self.centroids = [(random.random(),random.random()) for i in range(cluster_num)]

    def fit(self, datas):
        '''

        '''
        set_initial_centroids(datas)
        pass

    def fit_predict(self, datas):
        '''
        k個のクラスタを構築してdatasの各点が所属するクラスタインデックスを返す
        datasはlistのlistを想定
        '''
        set_initial_centroids(datas)
        old_centroids = self.centroids
        calc_belong_cluster(datas,self.centroids)

        pass

    def set_initial_centroids(self, datas):
        '''
        重心位置をデータの最大値に対する比率に変換する
        '''
        for centroid in self.centroids:
            centroid *= max(datas)

    def calc_belong_cluster(self, datas, centroids):
        '''
        各点が所属するクラスタを計算する
        '''
        for data in datas:
