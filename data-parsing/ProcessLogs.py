# Import the required libraries
import os           # Not used
import sys
import subprocess   # Not used
import shlex
import time
import json         # Not used
import yaml
import numpy as np
from tqdm import trange
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from IPython.display import display, HTML 
import LogConversion

if False:
    root = tk.Tk()
    root.withdraw()

    # Create a file dialog
    log_dir = filedialog.askdirectory(title="Select a directory")

    # Print the selected directory
    print(log_dir)

    # Close the root window
    root.destroy()
else:
    log_dir = '/Users/jfluhler/Library/CloudStorage/OneDrive-Personal/Documents/UAH Grad School/CS692/IKEV2_LOGS'



logs = Path(log_dir)

print(sum(1 for _ in logs.glob('*')))  # Files and folders, not recursive
print(sum(1 for _ in logs.rglob('*')))  # Files and folders, recursive

filesinfolder = sum(1 for x in logs.glob('*') if x.is_file())  # Only files, not recursive
totalfiles = sum(1 for x in logs.rglob('*') if x.is_file())  # Only files, recursive

print(("files in slected folder: " + str(filesinfolder)))
print(("files in slected folder and subfolders: " + str(totalfiles)))

print("\n\nList of log files in selected folder and subfolders:")
for x in logs.rglob('*.log'):
    print(x.name)


#runstats_temp = {'FileName': '', 'tc_cmd_str': '', 'tc_cmd': '', 'tc_cmd_arg': '', 'tc_interface': '', 'tc_type': '', 'tc_con1_name': '', 'tc_con1_val': '', 'AddParams': '', 'TotalTime': 0}
#runstats = pd.DataFrame(runstats_temp,0)

# Refomat the various runstats.txt log files into a single csv file:
# Input format is the log directory and the mode (write or append) for the csv file.

newlog = LogConversion.RunStats(log_dir,'w') # 
newlog = (log_dir + '/runstats.csv')

data = []
data2 = {}
data3 = []

with open(newlog) as f:
    for line in f:
        data.append(line)
        x = line.replace(':',': ').split(',')
        data2 = {}
        for y in x[:-1]:
            data2.update(yaml.safe_load(y))

        data3.append(data2)

RunStatsDF = pd.DataFrame(data3)

print("\n\nRunStatsDF:\n")
display(RunStatsDF[['TotalTime','IterationTime',
                    RunStatsDF.columns[9],
                    RunStatsDF.columns[10],
                    RunStatsDF.columns[11],]])


RunStatsDF['FullFilePath'] = RunStatsDF[['FilePath','FileName']].agg(''.join, axis=1)
display(RunStatsDF['FullFilePath'])


for log in RunStatsDF['FullFilePath']:
    LogConversion.get_Ike_State(log)







            
            



# Open the YAML config file
#with open(ymlConfig) as file:
#    YAMLConfig = yaml.safe_load(file)