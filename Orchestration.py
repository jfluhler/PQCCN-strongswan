# This is an optional file that can be used to orchestrate the 
#   entire data connection and analysis process.

## Orchestration.py
import os
import sys
import yaml
import numpy as np
from tqdm import trange
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from IPython.display import display, HTML 
from plotnine import *
import re
import time

from setuptools import setup, find_packages
packages=find_packages()

# Import local modules / functions
from data_collection import *    # Import the DataCollection.py file
from data_parsing import *    # Import the ProcessLogs.py file
from data_preparation import *    # Import the DataPreparation files
from data_analysis import *    # Import the Data Analysis files

# Manually Define the log directory
log_dir = '' #'../IKEV2_LOGS/JAMES'
ConfigFiles = ''

plvl = 2

if len(sys.argv) > 1:
    log_dir = sys.argv[1]
if len(sys.argv) > 2:
    ConfigFiles = sys.argv[2]

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

# Run the Data Collection Process
if False:
    if ConfigFiles == '':
        root = tk.Tk()
        root.withdraw()

        # Create a file dialog
        ConfigFiles = filedialog.askopenfilenames(title="Select Configuration Files")

        # Print the selected config files
        print(ConfigFiles)

        # Close the root window
        root.destroy()
    else:
        pass
    
    for ymlCFG in ConfigFiles:
        print("Processing Config File: " + ymlCFG + "\n\n")
        total_time = DataCollectCore.RunConfig(ymlCFG,(log_dir + '/'), 1)
        
    

# Process Raw Log Files save data into a DataFrame
if True:
    RunLogStatsDF = ProcessLogs.Log_stats(log_dir,plvl)
    if plvl >= 1:    
        DataFile = (log_dir + '/RunLogStatsDF.csv')
        RunLogStatsDF.to_csv(DataFile, index=False)
else:
    RunLogStatsDF = pd.read_csv(log_dir + '/RunLogStatsDF.csv')

display(RunLogStatsDF)

# Mark Log Files as Baseline or Post-Quantum
RunLogStatsDF = ProcessStats.MarkLogs(RunLogStatsDF,2)


# Save the DataFrame to a CSV files
DataFile = (log_dir + '/RunLogStatsDF.csv')
RunLogStatsDF.to_csv(DataFile, index=False)

# Generate Plots for the DataFrame and save to the log directory
Plotting.PlotVariParam(RunLogStatsDF,log_dir,2)





