from pathlib import Path
import pandas as pd
from IPython.display import display, HTML 
import numpy as np
from plotnine import *
import LogConversion

logfile = '/Users/jfluhler/Library/CloudStorage/OneDrive-Personal/Documents/UAH Grad School/CS692/IKEV2_LOGS/JAMES/charon.20240409_1556baseline_0.0-iter_1000.log'

ike_state_dict = LogConversion.get_Ike_State(logfile)

df = pd.DataFrame(ike_state_dict)

display(df)


EST = df.loc[(df.loc[:,"NewState"]=="ESTABLISHED"), :]
CON = df.loc[(df.loc[:,"NewState"]=="CONNECTING"), :]
Deltas = EST.Time.values - CON.Time.values

df.loc[(df.loc[:,"NewState"]=="ESTABLISHED"), ["Deltas"]] = Deltas

q75, q25 = np.percentile(Deltas, [75 ,25])
iqr = q75 - q25

Outliers = np.median(Deltas) + iqr

print(Outliers)

print(max(Deltas))

df.loc[(df.loc[:,"Deltas"]>=Outliers), "Deltas"] = Outliers*1.5

p1 = ggplot(df.loc[(df.loc[:,"NewState"]=="ESTABLISHED"),:], aes(x = 'Time', y = 'Deltas')) + geom_boxplot()
p2 = ggplot(df.loc[(df.loc[:,"NewState"]=="ESTABLISHED"),:], aes(x = 'Time', y = 'Deltas')) + geom_line()

ggsave(p1, filename=("plot1.png"))
ggsave(p2, filename=("plot2.png"))



