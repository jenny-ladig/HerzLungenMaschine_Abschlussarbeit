# Import external packages

from multiprocessing.connection import wait
import pandas as pd
from datetime import datetime
import numpy as np
import re

# Classes 

class Subject():
    def __init__(self, file_name):

        ### Aufgabe 1: Interpolation ###

        __f = open(file_name)
        self.subject_data = pd.read_csv(__f)
        self.subject_data = self.subject_data.interpolate(method='polynomial', order=2, axis=0)
        __splited_id = re.findall(r'\d+',file_name)      
        self.subject_id = ''.join(__splited_id)
        self.names = self.subject_data.columns.values.tolist()
        self.time = self.subject_data["Time (s)"]        
        self.spO2 = self.subject_data["SpO2 (%)"]
        self.temp = self.subject_data["Temp (C)"]
        self.blood_flow = self.subject_data["Blood Flow (ml/s)"]
        print('Subject ' + self.subject_id + ' initialized')



        

### Aufgabe 2: Datenverarbeitung ###

def calculate_CMA(df,n):  # Cumulative Moving Average mit Sliding Window (n=...), Window size becomes larger
       
#step 1: Importing data

  bloodflow = pd.read_csv("data1.csv", index_col='Time', parse_dates=True)
                                     
#step 2: Printing dataFrame
  bloodflow.head()

#step 3: only the column bloodflow
  bloodflow = bloodflow['Blood Flow (ml/s)'].to_frame()

#step 4: Calculate CMA with expanding method

  bloodflow['CMA'] = bloodflow['Blood Flow (ml/s)'].expanding().mean()
  bloodflow    #printing dataframe

#step 5: Plotting CMA

   bloodflow[['Bloodflow (ml/s)', 'CMA']].plot(label='RELIANCE', figsize=(16, 8))
                                  
    

def calculate_SMA(df,n):
    pass