# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 11:06:20 2022

@author: AVERKHO
"""

import pandas as pd
import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.preprocessing import StandardScaler

plsRegression=PLSRegression()

class CustomPLSRegression(PLSRegression):
    
    def __init__(self):
        
        super().__init__()
    
    def preprocess(self,X,y):
        
        scaler=StandardScaler()
               
        return scaler.fit_transform(X),scaler.fit_transform(y)
    
    def ssy(self,X,y,n_components=2):
        '''
        SSY calculation 
        Sum of squares of the Y block. For component number A, it is the Y residual Sum of Squares after component A.
        returns vector SSYcomp in the form 
        [Comp[0],Comp[1],...,Comp[A]]
    
        '''
        SS_total=np.dot(np.transpose(y),y)-1/len(y)*np.dot(np.transpose(y),np.dot(np.ones((len(y),len(y))),y))
        #print(SS_total)
        #print(y)
        SSY=[]
        
        for a in range(1,n_components+1):    
            model_=PLSRegression(a)
            model_.fit(X,y)
            pred_=model_.predict(X)
            #MSE(pred_,y)
            ss_sum=0
            for i in range(len(pred_)):
                
                ss_sum+=np.power((y[i]-pred_[i]),2)
            SSY.append(ss_sum[0])
        SSY=[SS_total]+SSY
        
        return SSY
    
    def VIP(self,weights,features,SSY):
            
            '''
            Computing VIPs
            Returning VIPs in the form of sorted DataFrame
            '''
            VIP=[]
            SSYcum=0
            for i in range(weights.shape[0]):
                for j in range(weights.shape[1]):
                    SSYcum+=weights.iloc[i][j]**2*SSY[j+1]
                    
            for i in range(weights.shape[0]): # iterating over rows
                var_sum=0
              
                for j in range(weights.shape[1]): # iterating over columns
                    var_sum+=weights.iloc[i][j]**2*SSY[j+1]
                
                vip=np.sqrt(weights.shape[0]*var_sum/SSYcum)
                VIP.append(vip)
            
            VIP=pd.DataFrame(VIP,index=features)
            VIP.columns=['VIP']
            VIP=VIP.sort_values(by='VIP',ascending=False)
        
            return VIP
    
    def getVips(self,X,y,cutoff='VIP',top=30):
        
        X_time=X['time']
        X=X.drop(columns=['time'])
        y=y.drop(columns=['time'])
        X_scaled,y_scaled=self.preprocess(X,y)
        
        self.fit(X_scaled,y_scaled)
        
        features=X.columns
        
        weights=pd.DataFrame(self.x_weights_)
        
        SSY=self.ssy(X_scaled,y_scaled)
        VIP=self.VIP(weights,features,SSY)
        
        VIP.reset_index(inplace=True)
        VIP=VIP.rename(columns={'index':'tag'},errors='ignore')
        
        #tags_={y:x for x,y in tags_.items()}
        
        
        #VIP['descriptor']=VIP['tag']#.str.lower()
        #VIP['descriptor']=VIP['descriptor'].map(tags_)
        
        return VIP.loc[:top]
    
    
        
        
        