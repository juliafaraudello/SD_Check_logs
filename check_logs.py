# Let's import the libraries needed.
from xlrd import open_workbook
import xlsxwriter
from datetime import date
import pandas as pd
import numpy as np
import os
import time
import warnings
from datetime import timedelta, datetime
from optparse import OptionParser
import glob
import requests

#Forecaster logs root
root_daily_log = r'C:\Users\zfaraude\Desktop\Develop\Check_logs\SD_forecaster_daily_logs.csv'
root_file_log = r'C:\Users\zfaraude\Desktop\Develop\Check_logs\File_log\*.xlsm'

#Check the last daily log file modification
def last_updated(root_daily_log):
    status= os.stat(root_daily_log)
    date = time.localtime(status.st_mtime)
    date = datetime(date[0], date[1], date[2], date[3], date[4], date[5])
    print ("The last modification of the daily log is at", date)
    return date

date_m= last_updated(root_daily_log)

#Create the data frame with the daily logs to check the cycles and rundate 
df = pd.read_csv(root_daily_log,header=0)
#print(df)
cycles=df.Cycle.unique()

rundate=df.RUNDATE.unique()
rundate = ''.join(rundate)
check_rundate = datetime.strptime(rundate, '%Y-%m-%d')

today = str(date.today())
today = datetime.strptime(today, '%Y-%m-%d')

#Check the last cycle and the amount of nodes
last_cycle= df.iat[-1, df.columns.get_loc("Cycle")]
count_nodes = df.apply(lambda x: x['Cycle'] == last_cycle, axis=1).sum()
print ("Cycles found in the daily log", cycles, " - Last cycle updated: ", last_cycle, " - Count Nodes: ", count_nodes, " - Rundate: ", rundate )

def check_deltas(df):
    #Select the last file log and create a dataframe
    list_of_files = glob.glob(root_file_log)
    list_of_files.sort(key=os.path.getctime,reverse=True)
    print('\n'.join(list_of_files))  
    file_name = list_of_files[-1]    # Last file from the folder
    print("lastFile:")
    print(file_name)
    df_file_log=pd.read_excel(file_name, sheet_name='LOG',header=0)

    #Filter Last cycle and UK for both data frame
    df_file_log=df_file_log[(df_file_log.Country == 'UK') & (df_file_log.Cycle == last_cycle)]
    df=df[(df.Country == 'UK') & (df.Cycle == last_cycle)]

    #Calculate the dif betwwen OFD_daily_log and OFD_forecaster_log
    dif_Expected_OFD= (df['Expected OFD '].sum() - df_file_log['Expected OFD '].sum())
    if (dif_Expected_OFD==0):
        aux_exit= True
    else:
        aux_exit= False
    return (aux_exit)


#Conditional, if rundate = today  and OFD_daily_log = OFD_forecaster_log execute the message to flex team, in case of false break the script
if (check_rundate == today) and (check_deltas(df)==True) :
    print("We don't have deltas and match today and rundate. An automatic message will now be sent.")
    text = "Logs created: " + str(date_m) + " - Cycle: " + str(last_cycle) + " @Present "
    payload = {'Content': text}
    #r = requests.post("https://hooks.chime.aws/incomingwebhooks/c6413541-f822-4fa1-8811-9a8c36a01531?token=YnExNXFVUWR8MXxPbHQwUHJMekpkTTZaMFVraXNPTWFSSm4wYVh3Ymgzb2I2dmwwZVowcGlV", json=payload)
else:
    print("Please check the daily log and the log file, we have deltas or don't match the rundate and today.")




