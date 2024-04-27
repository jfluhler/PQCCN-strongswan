import os

def getLogList(logdir : str, runstatPath : str) -> list[str]:
    file_names = []
    with open(runstatPath, 'r') as rsfile:
        rslines = rsfile.readlines()
        for line in rslines:
            line1 = line.split("/")
            line2 = line1[2].split(';')
            lineName = str(line2[0])
            file_names.append(lineName)
    return file_names

def getLogDelay(runstatPath : str) -> list[float]:
    logDelay = []
    with open(runstatPath, 'r') as rsfile:
        rslines = rsfile.readlines()
        for line in rslines:
            line1 = line.split("delay ")
            line2 = line1[1].split('ms')
            delay_i = float(line2[0])
            logDelay.append(delay_i)
    return logDelay

def getLogRuntime(runstatFile : str) -> list[float]:
    totalRunTimesList = []
    with open(runstatFile, 'r') as file:
        logData = file.readlines()
        for line in logData:
            lineA = line.split('Total Run Time: ')
            lineB = lineA[1].split(' seconds')
            totalRunTimesList.append(float(lineB[0]))
        return totalRunTimesList
    file.close()



def csvWriteResults(csvPath : str,fileNameList : list[str] , delayList : list[float], runtimelist : list[float]):
    with open(csvPath, 'w') as csvFile:
        for i in range(len(runtimelist)):
            lineToWrite = f"{fileNameList[i]},{str(delayList[i])},{str(runtimelist[i])}\n"
            csvFile.write(lineToWrite)
    csvFile.close()


def main():
    log_directory = r'C:\Users\Mitchell\Desktop\Logs'  # Update with the actual path to your log files
    runstats_path =  r'C:\Users\Mitchell\Desktop\Logs\runstats.txt'
    output_csv_path = r'C:\Users\Mitchell\Desktop\output.csv'

    log_list = getLogList(log_directory, runstats_path)
    logDelay_list = getLogDelay(runstats_path)
    logRuntime_list = getLogRuntime(runstats_path)

    csvWriteResults(output_csv_path, log_list, logDelay_list, logRuntime_list)




if __name__ == "__main__":
    main()