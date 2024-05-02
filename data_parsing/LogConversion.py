from pathlib import Path
import pandas as pd
import numpy as np

def get_Ike_State(logfile):
    ike_state = []
    ike_state_dict = {}
    with open(logfile, 'r') as f:
        for line in f.readlines():
            if 'state change:' in line:
                line = line.split()
                ike_state.append([line[0],line[4],line[7],line[9]])
                ike_state_dict.setdefault('Time', []).append(float(line[0]))
                ike_state_dict.setdefault('Connection', []).append(line[4])
                ike_state_dict.setdefault('OldState', []).append(line[7])
                ike_state_dict.setdefault('NewState', []).append(line[9])

    return ike_state_dict

def Get_Ike_State_Stats(df):

    EST = df.loc[(df.loc[:,"NewState"]=="ESTABLISHED"), :]
    CON = df.loc[(df.loc[:,"NewState"]=="CONNECTING"), :]

    Deltas = ''
    Q3 = np.nan
    Q1 = np.nan
    iqr = np.nan
    max = np.nan
    min = np.nan
    range = np.nan
    mean = np.nan
    median = np.nan
    stdDev = np.nan
    TotalConnections = 0
    ConnectionPercent = 0
    Outliers = np.nan

    if len(EST) <= len(CON):
        idx = np.linspace(0, len(EST.index)-1, len(EST.index)).astype(int)
        for i in idx:
            if i == 0:
                Deltas = EST.Time.values[i] - CON.Time.values[i]
            else:
                Deltas = np.append(Deltas, EST.Time.values[i] - CON.Time.values[i])
    else:
        print("More Established connections than attempted connections???")



    #Deltas = EST.Time.values - CON.Time.values

    #df.loc[(df.loc[:,"NewState"]=="ESTABLISHED"), ["Deltas"]] = Deltas
    if len(EST) <= len(CON):
        try:
            len(Deltas)
            if len(Deltas) > 0:
                Q3, Q1 = np.percentile(Deltas, [75 ,25])
                iqr = Q3 - Q1
                lower = Q1 - 1.5*iqr
                upper = Q3 + 1.5*iqr
                
                # Create arrays of Boolean values indicating the outlier rows
                upper_array = np.where(Deltas >= upper)[0]
                lower_array = np.where(Deltas <= lower)[0]
                drop_array = np.zeros(len(Deltas), dtype=bool)
                drop_array[upper_array] = True  # Set the upper outlier rows to True
                drop_array[lower_array] = True  # Set the lower outlier rows to True
                if sum(drop_array) < len(Deltas)/4:
                    keep_array = ~drop_array        # Invert the drop_array to get the keep_array
                else:
                    keep_array = np.ones(len(Deltas), dtype=bool) # Keep all rows if more than 25% are outliers
       

            max = np.max(Deltas)
            min = np.min(Deltas)
            range = max - min
            mean = np.mean(Deltas[keep_array])  # Only use the non-outlier rows
            median = np.median(Deltas)
            stdDev = np.std(Deltas[keep_array])
            Outliers = sum(drop_array)
            TotalConnections = len(Deltas)
        except:
            TotalConnections = len(EST.index)
            pass
        

        ConnectionPercent = len(EST.index)/(len(CON.index))



    LogStats = {'Q3': Q3, 'Q1': Q1, 'IQR': iqr, 'max': max, 'min': min, 'range': range,
                 'mean': mean, 'median': median, 'stdDev': stdDev, 'Outliers': Outliers, 
                 'TotalConnections': TotalConnections, 'ConnectionPercent': ConnectionPercent}

    return LogStats


def RunStats(log_dir, FileMode):
    count = 0;
    logs = Path(log_dir)
    if FileMode == 'w':
        with open((log_dir + '/runstats.csv'), 'w') as f:
            pass
            #write_line = 'FilePath,Source,FileName,TotalTime,IterationTime,tc_cmd_str,tc_cmd_arg,tc_interface,tc_type'
            #f.writelines(write_line + '\n')

        # Refomat the various runstats.txt log files into a single csv file:
    for x in logs.rglob('*.txt'):
        # print(str(x).removeprefix(log_dir))

        with open(x, 'r') as file:
            data = file.read()
            data = data.splitlines()
            for line in data:
                line = line.split(';')
                res = [i for i in line if 'tc_command' in i]
                res = str(res)
                res = res.removeprefix("['")
                res = res.removesuffix("']")
                tc_args = res.split()
                parameters = ''
                variParam = ''
                tc = ''
                if len(tc_args)>=3:
                    tc = tc + 'tc_cmd_arg: "' + tc_args[3] + '",'
                    if len(tc_args)>=5:
                        tc = tc + 'tc_interface: "' + tc_args[5] + '",'
                        if len(tc_args)>=7:
                            tc = tc + 'tc_type: "' + tc_args[7] + '",'
                            if len(tc_args)>=8:
                                variParam = 'VariParam: ' + '"' + tc_args[8] + '",'
                                for i in range(8, len(tc_args)-1,2):
                                    parameters = parameters + tc_args[i] + ': "' + tc_args[i+1] + '",'
                                

                # using list comprehension + in 
                # to get string with substring
                ts = ''
                res = [i for i in line if 'TotalTime' in i]
                res = str(res).split()
                if len(res) >= 2:
                    ts = res[2]
                else:
                    res = [i for i in line if 'TotalRunTime' in i]
                    res = str(res).split()
                    if len(res) >= 2:
                        ts = res[2]
                    
                res = [i for i in line if 'IterationTime' in i]
                res = str(res).split()
                if len(res) >= 2:
                    IterationTime = res[2]
                else:
                    IterationTime = ''

                runstats_temp = ','.join(['FilePath: ' + str(x.parent) + '/', 'Source: ' + str(x.name), \
                                        'FileName: ' + line[0].removeprefix('./'), 'TotalTime: ' + ts, 'IterationTime: ' + IterationTime,
                                        'tc_cmd_str: "' + line[2].replace('tc_command: ','') + '"',
                                        tc, variParam, parameters])
                runstats_temp = runstats_temp.replace(',,',',')
                runstats_temp = runstats_temp.replace(',,',',')
                runstats_temp = runstats_temp.replace(',,',',')
                #runstats_temp = str.join('FileName:' + line[0], 'tc_cmd_str:' + line[2], 'tc_cmd:' + tc_args[2], 'tc_cmd_arg:' + tc_args[3], 'tc_interface:' + tc_args[5], 'tc_type:' + tc_args[7], 'tc_con1_name:' + tc_args[8], 'tc_con1_val:' + tc_args[9], 'AddParams:' + (tc_args[10:len(tc_args)-1]), 'TotalTime:' + ts)
                #runstats = runstats.append(runstats_temp, ignore_index = True)
                #print(runstats_temp)

                with open((log_dir + '/runstats.csv'), 'a') as f:
                    f.writelines(runstats_temp + '\n')
                    count = count + 1;

    return (log_dir + '/runstats.csv')


            