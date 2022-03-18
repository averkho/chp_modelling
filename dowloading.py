# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 12:07:47 2022

@author: AVERKHO
"""
import pandas as pd
import numpy as np
import datetime as dt

import adodbapi as ado

class Servers:
    
    def __init__(self):
        
        pass
    
    def get_server_name(self,calc_mode):
        
        """
        The function for selecting server names by calculation mode
        """
        
        if calc_mode=='mean':
            return 'piavg'
        elif calc_mode=='std':
            return 'pistd'
        

class Download():
    
    def __init__(self):
        
        self.conn_str_PI=conn_str="Provider=PI OLE DB Provider;Data Source=SSVEPIP1;Initial Catalog=piarchive;Integrated Security=SSPI;SEssion ID=-1;\
            Command Timeout=600000; Connect Timeout = 1000000;"
            
            
    def __get_from_PI(self,transform=True,digstate=False):
        
        self.server=Servers().get_server_name(self.calc_mode)
        
        tag_dat=self.__get_tags()
        self.tags=list(tag_dat['tag'])
        
        descriptors=tag_dat
        sql_str=self.__get_sql_str()
        
        with ado.connect(self.conn_str_PI) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_str)
                        
                data=cur.fetchall()
                cols=cur.columnNames.keys()
                data=data.ado_results
                cols=cur.columnNames.keys()
                        
                dat_=pd.DataFrame(data).transpose()
                dat_.columns=cols
                dat_['time']=dat_['time'].dt.tz_convert(None)
                
                if transform:
                    DAT_=pd.DataFrame()
                            
                    for tag_ in dat_['tag'].unique():
                        if DAT_.shape[0]<1:
                            DAT_=dat_[dat_['tag']==tag_]
                                    
                            tag_to_reserve=tag_
                            if digstate:
                                DAT_=DAT_[['time','value','digstate']]
                            else:
                                        
                                DAT_=DAT_[['time','value']]
                        else:
                                    
                           DAT_[tag_]=dat_['value'][dat_['tag']==tag_].values
                    dat_=DAT_
                            
                    dat_=dat_.rename(columns={'value':tag_to_reserve},errors='ignore')
                            
               
            #dat=dat.drop(columns=['tag','descriptor','engunits'])
            dat_.reset_index(inplace=True,drop=True)        
                
        
        return dat_,descriptors
            
    def __get_sql_str(self):
        
        
        sql_str="""
            
            SELECT tag,value,time
            FROM {}
            WHERE tag in {}
            AND time BETWEEN '{}' AND '{}' AND timestep='{}'
        
            """.format(self.server,tuple(self.tags),self.start,self.finish,self.period)
            
        return sql_str
        
    def __get_tags(self,area='CHP'):
        
        
        sql_conn="""
        
                SELECT tag, descriptor, engunits, pointtypex
                FROM pipoint2
                WHERE tag LIKE '{}%' AND tag NOT LIKE '%RETIRED%' AND tag NOT LIKE '%Prof%' AND tag NOT LIKE '%Cognex%'
                      AND tag NOT LIKE '%meas%' AND tag NOT LIKE '%delta%' AND tag NOT LIKE '%Kytola%'
                      AND pointtypex in ('float32', 'int16', 'int32', 'float64', 'float16')
                """.format(area)
        
        with ado.connect(self.conn_str_PI) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_conn)
                data=cur.fetchall()
                data=data.ado_results
                cols=cur.columnNames.keys()
                dat=pd.DataFrame(data).transpose()
                dat.columns=cols
                
        return dat
    
    def get_data(self,start,finish=dt.datetime.today(),period='1H',calc_mode='mean'):
        
        self.start=start
        self.finish=finish
        self.period=period
        self.calc_mode=calc_mode
        
        dat,descriptors=self.__get_from_PI()
        
        return dat,descriptors
        

if __name__=="__main__":
    
    
    downloading=Download()
    dat,descriptors=downloading.get_data(start='01.02.2022')