## Plotting.py
# Path: data_analysis/Plotting.py
# Plotting is a module that contains functions to plot the logfile dataframe (RunLogStatsDF)

import pandas as pd
import numpy as np
import time
from plotnine import *
import re


def PlotVariParam(RunLogStatsDF,plot_dir,plvl):
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

                ggsave(meanplot, filename = file_name, path = plot_dir, dpi=600)
                
                if plvl > 1:
                    print("Save Plot: " + file_name)

                
                
