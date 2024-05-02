## ProcessStats.py
# Path: data_preparation/ProcessStats.py
# Process Stats is a module that contains functions to the logfile dataframe (RunLogStatsDF) 

def MarkLogs(DF,plvl):
    # Mark Logs looks for the string 'baseline' in the logs and marks it as as Baseline (Ture /False)
    # It also marks the Algorithm as Diffie-Helman or PostQuantum

    # Define a search function
    def search_string(s, search):
        return search in str(s).lower()

    # Search for the string 'al' in all columns
    Bmask = DF.apply(lambda x: x.map(lambda s: search_string(s, 'baseline'.lower())))
    DHmask = DF.apply(lambda x: x.map(lambda s: search_string(s, 'DH'.lower())))
    
    # Add column to DataFrame based on the mask
    DF['Baseline'] = Bmask.any(axis=1)
    DF['Algorithm'] = Bmask.any(axis=1)
    
    if sum(Bmask.any(axis=1)==True) == 0:
        print('No Baseline Found, switching to DH as Baseline')
        DF['Baseline'] = DHmask.any(axis=1)
        DF['Algorithm'] = DHmask.any(axis=1)
        



    DF = DF.replace({'Algorithm': {True: 'Diffie-Helman', False: 'PostQuantum'}})
    
    return DF