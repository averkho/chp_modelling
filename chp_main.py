# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 13:28:58 2022

@author: AVERKHO
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.close('all')
from dowloading import Download
from preprocessing import DataPreprosessing

from sklearn.metrics import mean_squared_error

import os

y_tag='CHP-MKA10CE010.PV'

print(os.listdir('./'))

import lightgbm as lgb

def train_test_split(dat,splitting=0.33):
    
    train=dat[:int(dat.shape[0]*(1-splitting))]
    test=dat[int(dat.shape[0]*(1-splitting)):]
    
    
    X_train=train.drop(columns=['time',y_tag])
    y_train=train[y_tag]
    
    X_test=test.drop(columns=['time',y_tag])
    y_test=test[y_tag]
    
    return X_train,X_test,y_train,y_test


def plotting(dat_pred,mse,model,i):
    
    fig=plt.figure(i)
    ax=fig.add_subplot(111)
    ax.plot(dat_pred['fact'],label='fact',color='blue')
    ax.plot(dat_pred['predicted'],label='predicted',color='red')
        
    ax.axvline(dat_pred[dat_pred['label']=='train'].shape[0])
    
    ax.set_title('Model {} with train mse={} and test mse={}'.format(model,mse['mse_train'],mse['mse_test']))
    ax.set_ylabel('MW')
    ax.legend(loc='best')
    
    
    

def lightgbm_regresion(dat):
    
    X_train,X_test,y_train,y_test=train_test_split(dat)
    
    lgb_regr=lgb.LGBMRegressor()
    lgb_regr.fit(X_train,y_train)
    
    pred_train=lgb_regr.predict(X_train)
    pred_test=lgb_regr.predict(X_test)
    
    mse={'mse_train':np.round(mean_squared_error(pred_train,y_train),2),
         'mse_test':np.round(mean_squared_error(pred_test,y_test),2)}
    
    dat_pred_test=pd.DataFrame(pred_test,columns=['predicted'])
    dat_pred_test['fact']=y_test.values
    dat_pred_test['label']='test'
    
    dat_pred_train=pd.DataFrame(pred_train,columns=['predicted'])
    dat_pred_train['fact']=y_train.values
    dat_pred_train['label']='train'
    
    dat_pred=pd.concat([dat_pred_train,dat_pred_test])
    dat_pred.reset_index(inplace=True)
    
    plotting(dat_pred,mse,model='lghtgbm',i=2)
    

if __name__=="__main__":
    
    download=Download()
    preprocess=DataPreprosessing()
    
    dat,descriptors=download.get_data(start='01.02.2022')
    
    y_tag='CHP-MKA10CE010.PV'
    
    dat,_,_=preprocess.preprocess_data(dat,y_value=y_tag)
    
    lightgbm_regresion(dat)
    
    
    
    
    
    
    
    
    
    
    
    