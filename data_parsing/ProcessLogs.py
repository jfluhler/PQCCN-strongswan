## ProcessLogs.py
# Path: data_parsing/ProcessLogs.py
# This file is used to process the log files and generate statistics.
# if plvl = 0, then no output is generated.
# if plvl = 1, then a csv of the dataframe is saved to the parent logfile directory
# 

# Import the required libraries
import yaml
import numpy as np
from tqdm import trange
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from IPython.display import display, HTML 

# Import local modules / functions
from data_parsing.LogConversion import * # Import the LogConversion.py file

def Log_stats(log_dir,plvl):

    print("Starting Log_stats")

    if log_dir == '':
        root = tk.Tk()
        root.withdraw()

        # Create a file dialog
        log_dir = filedialog.askdirectory(title="Select a directory")

        # Print the selected directory
        print(log_dir)

        # Close the root window
        root.destroy()
    else:
        pass
        # log_dir = '/IKEV2_LOGS'

    logs = Path(log_dir)

    filesinfolder = sum(1 for x in logs.glob('*') if x.is_file())  # Only files, not recursive
    totalfiles = sum(1 for x in logs.rglob('*') if x.is_file())  # Only files, recursive

    if plvl >= 1:
        print(("files in slected folder: " + str(filesinfolder)))
        print(("files in slected folder and subfolders: " + str(totalfiles)))

    if plvl >= 2:
        print("\n\nList of log files in selected folder and subfolders:")
        for x in logs.rglob('*.log'):
            print(x.name)

    # Refomat the various runstats.txt log files into a single csv file:
    # Input format is the log directory and the mode (write or append) for the csv file.
    newlog = RunStats(log_dir,'w') # 
    # newlog is going to be log_dir + '/runstats.csv'

    data = []
    data2 = {}
    data3 = []

    with open(newlog) as f:
        for line in f:
            data.append(line)
            line = line.replace(':',': ')
            line = line.replace(': /',':/')
            x = line.replace(': \\',':\\').split(',')
            data2 = {}
            for y in x[:-1]:
                data2.update(yaml.safe_load(y))

            data3.append(data2)

    RunStatsDF = pd.DataFrame(data3)

    if plvl >= 2:
        print("\n\nRunStatsDF:\n")
        display(RunStatsDF[['TotalTime','IterationTime']])


    RunStatsDF['FullFilePath'] = RunStatsDF[['FilePath','FileName']].agg(''.join, axis=1)
    if plvl >= 2:
        print("\n\nRunStatsDF 'FulleFilePath':\n")
        display(RunStatsDF['FullFilePath'])

    Ike_State_Stats = pd.DataFrame()
    LogStats = {}

    # Loop through the RunStatsDF and get the IKE state stats
    #   and perform the stats for each log file
    for log in RunStatsDF['FullFilePath']:
        # Get the IKE state time series data
        ike_state_dict = get_Ike_State(log)
        df = pd.DataFrame(ike_state_dict)

        # Get the IKE state stats (mean, median, etc.)
        LogStats['FullFilePath'] = log
        LogStats.update(Get_Ike_State_Stats(df))
        if len(Ike_State_Stats.columns) == 0:
            Ike_State_Stats = pd.DataFrame(LogStats, index=[0])
        else:
            Ike_State_Stats = pd.concat([Ike_State_Stats, pd.DataFrame(LogStats, index=[0])], axis=0)

    # Merge the RunStatsDF with the IKE state stats
    RunLogStatsDF = RunStatsDF.merge(Ike_State_Stats, how='inner', on='FullFilePath')  

    # Save the RunStatsDF to a csv file
    if plvl > 2:
        print("\n\nRunLogStatsDF:\n")
        display(RunLogStatsDF)
        print("\n\nSaving RunLogStatsDF to a csv file.")

    return RunLogStatsDF