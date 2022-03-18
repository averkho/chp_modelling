# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 15:38:55 2021

@author: averkho
"""
import pandas as pd
import numpy as np

from tqdm import tqdm

from scipy.stats import pearsonr

class DataPreprosessing():
    
    def __init__(self,preprocessing=True,filling_nan=True,removing_outliers=True,standardization=True):
        
        self.preprocessing=preprocessing
        self.filling_nan=filling_nan
        self.removing_outliers=removing_outliers
        self.standardization=standardization
        self.correlation_coef_threshold=0.95
    
    def __fil_nan(self,df,how='median'):
    
        for i,col in tqdm(enumerate(df.columns[1:])):
            
            ss=df[col][df[col].apply(lambda x: isinstance(x,str))].unique()
            df[col]=df[col].replace(ss,np.nan)
            if how=='median':
                median=df[col].median()
                df[col]=df[col].fillna(median)
        return df

    def __oulier_removal_dat(self,df):
        """ Removal outliers based on quartiles on dataframe level """
    
        def remove_outliers(d,interval=2):
            Q1=d.quantile(0.25)
    
            Q3=d.quantile(0.75)
    
            IQR=Q3-Q1
    
            median=d.median()
            Lower_fence=Q1-(interval*IQR)
            Upper_fence=Q3+(interval*IQR)
    
            d=d.apply(lambda x: median if x<Lower_fence or x>Upper_fence else x)
    
            return d
        for i,col in tqdm(enumerate(df.columns[3:])):
    
            df[col]=remove_outliers(df[col])
        
        return df    
    
    def __remove_duplicates(self,df):
        return df.loc[:,~df.columns.duplicated()]
    
    def __remove_missing(self,df,missing_level=50):
        
        """ removing columns with predefined level of missing values.
        And returning corrected DataFrame plus the list of deletd columns
        """
        cols_to_delete=[]
        for i in range(df.shape[1]):
            if (df[df.columns[i]].isnull().sum()>0):
                if (df[df.columns[i]].isnull().sum()/df.shape[0]*100>missing_level):
                    cols_to_delete.append(df.columns[i])
        df=df.drop(columns=cols_to_delete)
        return df,cols_to_delete
    
    def __remove_the_same_parameters(self,df,y_value):
        '''
        

        Parameters
        ----------
        df : DataFrame of parameters
            DESCRIPTION.
        y_value : string
            y_value name.
            
        The function seaks and removes from DataFrame the paramaters which correlation coefficient is above threshold.
        The idea behind this is that exremly high correlation means that the parameters are the same. 
        Returns
        -------
        df : TYPE
            DESCRIPTION.
        same_parameters : TYPE
            DESCRIPTION.

        '''
        y=df[y_value]
        
        X=df
        X=X.drop(columns=[y_value])
        cols_to_drop=[col for col in X.columns if 'time' in col]
        X=X.drop(columns=cols_to_drop)
        #X=X.drop(columns=['timestamp'])
        print('I am heer')
        same_parameters=[]
        
        for col in X.columns:
            x=X[col].astype('float')
            
            corr=np.abs(np.corrcoef(x,y)[0][1])
            
            if corr>=self.correlation_coef_threshold:
                same_parameters.append(col)
        
        df=df.drop(columns=same_parameters) 
        
        print('I am heer debug')
        return df,same_parameters
    
    def __remove_zero_var_data(self,dat):
        
        cols_to_drop=[]
        
        cols=dat.columns
        
        cols=[col for col in cols if col!='time']
        
        for col in cols:
            
            dat[col]=dat[col].astype('float')
           
            
            if (np.std(dat[col])==0):
                cols_to_drop.append(col)
        
        dat=dat.drop(columns=cols_to_drop)
        
        return dat
    
    
    def preprocess_data(self,dat,y_value=None):
        
        """
        Main funcion for data preprocessing
        
        Input parameters 
        dat - DataFrame with all values
        y_value - tag of y value
        
        """
        
        print('Duplicate removal start')
        df=self.__remove_duplicates(dat)
        print('Duplicate removal finished')
        
        print('NAN removal start')
        df=self.__fil_nan(dat)
        print('NAN removal finished')
        
        print('Missing removal start')
        dat,deleted_columns=self.__remove_missing(dat)
        print('Missing removal finished')        
        
        print('Outlier removal start')
        dat=self.__oulier_removal_dat(dat)
        print('Outlier removal finished')
        
        print("Zero values removal start")
        dat=self.__remove_zero_var_data(dat)
        print("Zero values removal finish")
        
        if y_value:
           
            dat,same_parameters=self.__remove_the_same_parameters(dat,y_value)
            return dat,deleted_columns,same_parameters
        
        #dat=dat.astype(float)
        
        return dat,deleted_columns
    
    
    
    
    
    
    
    
    
    
    