from pathlib import Path

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
                tc = ''
                if len(tc_args)>=3:
                    tc = tc + 'tc_cmd_arg: "' + tc_args[3] + '",'
                    if len(tc_args)>=5:
                        tc = tc + 'tc_interface: "' + tc_args[5] + '",'
                        if len(tc_args)>=7:
                            tc = tc + 'tc_type: "' + tc_args[7] + '",'
                            if len(tc_args)>=8:
                                for i in range(8, len(tc_args)-1,2):
                                    parameters = parameters + tc_args[i] + ': "' + tc_args[i+1] + '",'

                # using list comprehension + in 
                # to get string with substring
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
                                        tc, parameters])
                runstats_temp = runstats_temp.replace(',,',',')
                #runstats_temp = str.join('FileName:' + line[0], 'tc_cmd_str:' + line[2], 'tc_cmd:' + tc_args[2], 'tc_cmd_arg:' + tc_args[3], 'tc_interface:' + tc_args[5], 'tc_type:' + tc_args[7], 'tc_con1_name:' + tc_args[8], 'tc_con1_val:' + tc_args[9], 'AddParams:' + (tc_args[10:len(tc_args)-1]), 'TotalTime:' + ts)
                #runstats = runstats.append(runstats_temp, ignore_index = True)
                #print(runstats_temp)

                with open((log_dir + '/runstats.csv'), 'a') as f:
                    f.writelines(runstats_temp + '\n')
                    count = count + 1;

    return (log_dir + '/runstats.csv')


            