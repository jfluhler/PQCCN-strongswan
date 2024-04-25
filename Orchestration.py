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
# from data_collection import *    # Import the DataCollection.py file
from data_parsing import *    # Import the ProcessLogs.py file
# from data_preparation import *    # Import the DataPreparation files
# from data_analysis import *    # Import the Data Analysis files

# Manually Define the log directory
log_dir = '' #'../IKEV2_LOGS/JAMES'

plvl = 2

if len(sys.argv) > 1:
    log_dir = sys.argv[1]

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


if True:
    RunLogStatsDF = ProcessLogs.Log_stats(log_dir,plvl)
    if plvl >= 1:    
        DataFile = (log_dir + '/RunLogStatsDF.csv')
        RunLogStatsDF.to_csv(DataFile, index=False)
else:
    RunLogStatsDF = pd.read_csv(log_dir + '/RunLogStatsDF.csv')

display(RunLogStatsDF)



# Define a search function
def search_string(s, search):
    return search in str(s).lower()

# Search for the string 'al' in all columns
mask = RunLogStatsDF.apply(lambda x: x.map(lambda s: search_string(s, 'baseline')))

# Add column to DataFrame based on the mask
RunLogStatsDF['Baseline'] = mask.any(axis=1)
RunLogStatsDF['Algorithm'] = mask.any(axis=1)

RunLogStatsDF = RunLogStatsDF.replace({'Algorithm': {True: 'Diffie-Helman', False: 'PostQuantum'}})

# Re Save the DataFrame to a CSV file
DataFile = (log_dir + '/RunLogStatsDF.csv')
RunLogStatsDF.to_csv(DataFile, index=False)

for varp in RunLogStatsDF['VariParam'].unique().tolist():
    print(varp)
    if pd.notnull(varp):
        if plvl > 2:
            print(RunLogStatsDF[varp][(RunLogStatsDF['VariParam']==varp)])

        tmpdf = RunLogStatsDF[(RunLogStatsDF['VariParam']==varp)]

        tmpdf[(tmpdf['Baseline']==True)]['Legend'] = 'Diffie-Helman'
        tmpdf[(tmpdf['Baseline']==False)]['Legend'] = 'Post-Quantum'

        newcol = [varp + 'val']

        tmpdf.loc[:,newcol] = tmpdf.loc[:,varp].apply(lambda x: re.search(r'\d+', x).group(0) if pd.notnull(x) else np.nan).astype(float)

        tmpdf = tmpdf.sort_values(newcol)
    

        minval = tmpdf[newcol].min().values[0].astype(float)
        maxval = tmpdf[(tmpdf['Baseline']==False)][newcol].max().values[0].astype(float)

        xbreaks = np.linspace(minval, maxval, 10).astype(float).tolist()

        strbreaks = []

        for i in range(len(xbreaks)):
            strbreaks.append(round(xbreaks[i],2))

        selected_stats = ['mean','median','ConnectionPercent','IterationTime']

        for stat in selected_stats:

            minval_y = tmpdf[stat].min().astype(float)
            highmed = max(tmpdf[(tmpdf['Baseline']==False)][stat].median(), tmpdf[(tmpdf['Baseline']==True)][stat].median())
            maxval_y = tmpdf[(tmpdf['Baseline']==False)][stat].max().astype(float)

            if maxval_y < highmed:
                maxval_y = maxval_y + highmed

            if stat == 'ConnectionPercent':
                minval_y = 0
                maxval_y = 100
                tmpdf[stat] = tmpdf[stat] * 100

            minval_y = minval_y - (minval_y * 0.2)
            maxval_y = maxval_y + (maxval_y * 0.2)
        
            meanplot = ggplot(tmpdf) + aes(x=newcol[0], y=stat, color='Algorithm') \
            + geom_point() \
            + labs(title=[str(varp) + ' vs. ' + stat], x=varp, y=stat) \
            + scale_x_continuous(breaks=(strbreaks), limits=([minval,maxval])) \
            + scale_y_continuous(limits=([minval_y,maxval_y])) \
            + scale_color_manual(values=(['#0077C8','#E69F00']))

            #plot2.show()
            date_time = time.strftime("%Y%m%d_%H%M")
            file_name = (date_time + "_" + varp + '_vs_' + stat + '.png')

            ggsave(meanplot, filename = file_name, path = log_dir, dpi=600)






# display(RunLogStatsDF)



