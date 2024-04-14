## Core Data Collection Script
#  This script is the core data collection script for the PostQuantumIKEv2 project.
#  The script is designed to be run on a host machine and will interact with Docker
#  to start and stop containers. The script will also interact with the containers
#  to enable qdisc for tc, and to start strongswan the charon deamon. 
#  The script then invokes a loop to change the tc constraints
#  an inner loop then initiates and terminates the IPSEC connection a defined number of times. 
#  once the IPSEC loop is complete the script will update the tc constraints and repeat the process.
#  Once the tc constraint range has been covered, script will copy the charon log files 
#  from the Carol container to the host machine. The script will also log the run stats to a file. 
#  Finally the script will also remove all qdisc constraints and stop the containers.
#
#  To run the script, the user must provide a YAML configuration file.
#  this can be passed to python as an argument in the terminal or the default file will be used.
#  The default file is DataCollect_baseline.yaml but can be changed in the code below.
#
#  Example terminal command: python3 DataCollectCore.py DataCollect_baseline.yaml
#


# Import the required libraries
import os           # Not used
import sys
import subprocess   # Not used
import shlex
import time
import json         # Not used
import yaml
import numpy as np
from python_on_whales import DockerClient
from tqdm import trange

if len(sys.argv) > 1:
    ymlConfig = sys.argv[1]
else:
    ymlConfig = "./DataCollect_baseline.yaml"
    # ConfigFile = "DataCollect_bandwidth.json"


## IMPORT CONFIGURATION FILE
# Open the JSON file
# with open('PostQuantumIKEv2/' + ConfigFile) as file:
#     JSONConfig = json.load(file)

# Open the YAML config file
with open(ymlConfig) as file:
    YAMLConfig = yaml.safe_load(file)

# Breakup the JSON file into different dictionaries
# JCoreConfig = JSONConfig.get('CoreConfig')
# JCarolConfig = JSONConfig.get('Carol_TC_Config')
# JMoonConfig = JSONConfig.get('Moon_TC_Config')

CoreConfig = YAMLConfig.get('CoreConfig')
CarolConfig = YAMLConfig.get('Carol_TC_Config')
MoonConfig = YAMLConfig.get('Moon_TC_Config')

# Define the maximum run time
if bool(CoreConfig['MaxTimeS']):
    max_run_time = CoreConfig['MaxTimeS']
else:
    max_run_time = 3600  # 3600 seconds is 1 hour

# Define the print level  
if bool(CoreConfig['PrintLevel']): 
    pLvl = CoreConfig['PrintLevel']
else:
    pLvl = 1

# Define the local path to save the log files
if bool(CoreConfig['LocalPath']):
    LOG_LocalPath = CoreConfig['LocalPath']
else:
    LOG_LocalPath = "./"

# Define the remote path of the charon log files
if bool(CoreConfig['RemotePath']):
    RemotePath = CoreConfig['RemotePath']
else:
    RemotePath = "/var/log/charon.log"

# Define the location and name of the Docker Compose File
if bool(CoreConfig['compose_files']):
    DockerComposeFile = CoreConfig['compose_files']
else:
    DockerComposeFile = ["./strongX509/pq-strongswan/docker-compose.yml"]
    

if pLvl > 0:
    # Print the dictionary values
    print("\n\nCORE CONFIG")
    for x in CoreConfig:
        print("\t" + x + ':', CoreConfig[x])

    # Because the Carol and Moon dictionaries are nested, 
    #  we need to loop through the top level and the nested levels to print
    print("\n\nCAROL CONFIG")
    if bool(CarolConfig):
        for x, obj in CarolConfig.items():
            print("\t" + x)

            for y in obj:
                print("\t\t" + y + ':', obj[y])

    print("\n\nMOON CONFIG")
    if bool(MoonConfig):
        for x, obj in MoonConfig.items():
            print("\t" + x)

            for y in obj:
                print("\t\t" + y + ':', obj[y])



print("\n\n -----------------------------------------------")
print("Max Run Time: " + str(max_run_time/60) + " minutes")
print("----------------------------------------------- \n\n")

# Define the Docker Client
docker = DockerClient(compose_files=DockerComposeFile)
docker.compose.ps()

## SET TO FALSE IF DOCKER AND CHARON ARE ALREADY RUNNING
FreshRun = False

if FreshRun == False:
    ## Stop Docker Containers (incase any are running)
    docker.compose.down()

    ## Start Docker Containers
    if pLvl > 0:
        print(" -- Starting Docker Containers -- ")
    # Start the Docker Containers    
    docker.compose.up(detach=True)

    # Wait for the containers to start, probably not needed at all
    time.sleep(5)
else:
    print("Use Existing Containers") #docker.compose.restart()

if True == True:
    # Access Carol & moon to enable qdisc
    if pLvl > 0:
        print(" -- Enable qdisc in Carol & Moon -- ")
    docker.execute("carol", shlex.split("ip link set eth0 qlen 1000"))
    docker.execute("moon", shlex.split("ip link set eth0 qlen 1000"))

    # Enable moon to accept IPSEC connections
    if pLvl > 0:
        print(" -- Enable .charon deamon on moon-- ")
    docker.execute("moon", shlex.split("./charon"), detach=True)
    docker.execute("moon", shlex.split("swanctl --list-conns"))

    #Start Logging (Charon)
    if pLvl > 0:
        print(" -- Enable .charon deamon on Carol-- ")
    docker.execute("carol", shlex.split("./charon"), detach=True)
    docker.execute("carol", shlex.split("swanctl --list-conns"))


    # Access Carol and add starting TC Constrains
    # Because the Carol and Moon dictionaries are nested, 
    #  we need to loop through the top level and the nested levels to print
    
    C_ctype = ''
    C_constraint = ''
    C_interface = ''
    C_Min = 1
    C_Max = 1
    C_units = ''
    C_steps = 1
    C_AddParams = ''

    M_ctype = ''
    M_constraint = ''
    M_interface = ''
    M_Min = 1
    M_Max = 1
    M_units = ''
    M_steps = 1
    M_AddParams = ''

    tc_string = ''

    # if there are constraints in the Carol Config then add them
    if bool(CarolConfig):
        # Assign starting TC Constrains to variables
        for x, obj in CarolConfig.items():
            # First Constraint should be the adjustable constraint
            if x == 'Constraint1':
                C_ctype = obj['Type']
                C_constraint = obj['Constraint']
                C_interface = obj['Interface']
                C_Min = obj['StartRange']
                C_Max = obj['EndRange']
                C_units = obj['Units']
                C_steps = obj['Steps']
                if bool(obj['AddParams']):
                    C_AddParams = obj['AddParams']

                # Build the tc command string
                tc_string = ("tc qdisc " + "add" + " dev " + C_interface + " root " + C_ctype + " " +  
                    C_constraint + " " + str(C_Min) + C_units + " " + C_AddParams)

                if pLvl > 1:
                    print("Carol Starter Adjustable Constraint: " + tc_string)

                # Execute the tc command    
                docker.execute("carol", shlex.split(tc_string))

                # If MirrorMoon is True then execute the same command on Moon
                if CoreConfig['MirrorMoon'] == True:
                    docker.execute("moon", shlex.split(tc_string))

            else:
                # If there are additional static constraints listed
                tmp_ctype = obj['Type']
                tmp_constraint = obj['Constraint']
                tmp_interface = obj['Interface']
                tmp_Min = obj['StartRange']
                tmp_units = obj['Units']
                if bool(obj['AddParams']):
                    tmp_AddParams = obj['AddParams']
                else:
                    tmp_AddParams = ''

                
                # Check the type of constraint
                if tmp_ctype == C_ctype:
                    # If the constraint type is the same then we need to tack on the additional constraints to the primary constraint
                    # for example if we are using netem on both constraints (for example delay and loss)
                    # then we cannot add both. Instead we combine them into one command and update AddParams with the 
                    # additional constraints. Then we need replace the previous constraint
                    # tc qdisc replace dev eth0 root netem delay 200ms loss 10%
                    # Really the perefered placement for additional static constraints would be the the AddParams field.

                    C_AddParams = (C_AddParams + " " + tmp_constraint + " "  + str(tmp_Min) + tmp_units + " " + tmp_AddParams)

                    if pLvl > 1:
                        print("Warning: New Constraint Type is the same as the adjustable constraint:" + tmp_ctype)
                    tc_string = ("tc qdisc " + "replace" + " dev " + C_interface + " root " + C_ctype + " " +  
                        C_constraint + " " + str(C_Min) + C_units + " " + C_AddParams)
                else:
                    tc_string = ("tc qdisc add dev " + tmp_interface + " root " + tmp_ctype + " " + 
                        tmp_constraint + " " + str(tmp_Min) + tmp_units + " " + tmp_AddParams)
                
                

                # Execute the tc command
                docker.execute("carol", shlex.split(tc_string))
                if pLvl > 1:
                    print("Carol Starter Constraint: " + tc_string)

                # If MirrorMoon is True then execute the same command on Moon
                if CoreConfig['MirrorMoon'] == True:
                    docker.execute("moon", shlex.split(tc_string))
                    if pLvl > 1:
                        print("Carol Starter Constraint Mirrored on Moon:" + tc_string)
                

    # Access Moon and add starting TC Constrains
    if bool(MoonConfig):
        for x, obj in MoonConfig.items():
            # First Constraint should be the adjustable constraint (though currently the code only adjust constraints on carol)
            if x == 'Constraint1':
                M_ctype = obj['Type']
                M_constraint = obj['Constraint']
                M_interface = obj['Interface']
                M_Min = obj['StartRange']
                M_Max = obj['EndRange']
                M_units = obj['Units']
                M_steps = obj['Steps']
                if bool(obj['AddParams']):
                    M_AddParams = obj['AddParams']

                # Build the tc command string
                tc_string = ("tc qdisc add dev " + M_interface + " root " + M_ctype + " " +  
                    M_constraint + " " + str(M_Min) + M_units + " " + M_AddParams)

                if pLvl > 1:
                    print("Moon Starter Adjustable Constraint: " + tc_string)

                # Execute the tc command    
                docker.execute("moon", shlex.split(tc_string))

            else:
                # If there are additional static constraints listed
                tmp_ctype = obj['Type']
                tmp_constraint = obj['Constraint']
                tmp_interface = obj['Interface']
                tmp_Min = obj['StartRange']
                tmp_units = obj['Units']
                if bool(obj['AddParams']):
                    tmp_AddParams = obj['AddParams']
                else:
                    tmp_AddParams = ''

                # Check the type of constraint
                if tmp_ctype == M_ctype:
                     # If the constraint type is the same then we need to tack on the additional constraints to the primary constraint
                    # for example if we are using netem on both constraints (for example delay and loss)
                    # then we cannot add both. Instead we combine them into one command and update AddParams with the 
                    # additional constraints. Then we need replace the previous constraint
                    # tc qdisc replace dev eth0 root netem delay 200ms loss 10%
                    # Really the perefered placement for additional static constraints would be the the AddParams field.

                    M_AddParams = (M_AddParams + " " + tmp_constraint + " "  + str(tmp_Min) + tmp_units + " " + tmp_AddParams)

                    if pLvl > 1:
                        print("Warning: New Constraint Type is the same as the adjustable constraint:" + tmp_ctype)
                    
                    # Build the tc command string with replace
                    tc_string = ("tc qdisc " + "replace" + " dev " + M_interface + " root " + M_ctype + " " +  
                        M_constraint + " " + str(M_Min) + M_units + " " + M_AddParams)
                    
                else:
                    # Build the tc command string with add
                    tc_string = ("tc qdisc add dev " + tmp_interface + " root " + tmp_ctype + " " + 
                        tmp_constraint + " " + str(tmp_Min) + tmp_units + " " + tmp_AddParams)

                if pLvl > 1:
                        print("Moon Starter Constraint: " + tc_string)

                # Execute the tc command on moon
                docker.execute("moon", shlex.split(tc_string))

# Wait for the containers to have all settings applied.
time.sleep(1)

# Start Run Timer
if pLvl > 0:
    print(" -- Starting Data Collection Run -- ")

# Start the run timer
startrun_tic = time.perf_counter()


# Calculate a linear range of values for Carol Constraint 1

C_vals = np.round(np.linspace(C_Min, C_Max, C_steps), 2)

if pLvl > 0:
    print(" -- Begin Constraint 1 Loop -- ")

if pLvl > 0:
    print("Total Planned Iterations: " + str(len(C_vals)))
    print("Planned Values for Carol Constraint " + C_constraint + ": " + str.replace(str(C_vals)," ",",") + "\n\n")

#START Constraint 1 Loop
for i in trange(len(C_vals)):
    
    
    #Start Wireshark Logging

    # Start Internal Timer for Constraint 1 Loop
    L1_tic = time.perf_counter()

    # Update Carol Constraints (change)
    if bool(CarolConfig):
        tc_string = ("tc qdisc change dev " + C_interface + " root " + C_ctype + " " + 
            C_constraint + " " + str(C_vals[i]) + C_units + " " + C_AddParams)
    
        # Execute the tc command
        docker.execute("carol", shlex.split(tc_string))
        if pLvl > 2:
            print("Updated Carol With: " + tc_string)

        if CoreConfig['MirrorMoon'] == True:
            # Update Moon Constraints (change) to match carol
            docker.execute("moon", shlex.split(tc_string))
            if pLvl > 2:
                print("Updated Moon With: " + tc_string)


    # START Single Constraint Function
    # IPSEC LOOP N TIMES
    ipsec_N = CoreConfig['TC_Interations']
    if pLvl > 2:
        print(" -- Begin IPSec Loop -- ")
    for j in trange(ipsec_N):

        
        try:
            # Initiate IPSEC Connection
            if pLvl > 3:
                print("swanctl --initiate --child net")

            docker.execute("carol", shlex.split("swanctl --initiate --child net"))
        except:
            if pLvl > 1:
                print("Possible Error initiating IPSEC Tunnel ")

        try:
            # Send data file
            docker.execute("carol", shlex.split("ping -c 2 strongswan.moon.com"))
        except:
            if pLvl > 1:
                print("Possible Error sending data in Tunnel ")

        try:
            # Deactivate IPSEC Connection
            if pLvl > 3:
                print("swanctl --terminate --ike home")

            docker.execute("carol", shlex.split("swanctl --terminate --ike home"))
        except:
            if pLvl > 1:
                print("Possible Error terminating IPSEC Tunnel")

        # Check timer if > max time break loop
        if time.perf_counter() - startrun_tic > max_run_time:
            break
        else:
            continue
    # END IPSEC LOOP 
    # END Single Constraint Function

    #Stop Wireshark Logging



    ## Move Data Files from Carol to local machine (or volume) and rename
    # Create date_time string
    date_time = time.strftime("%Y%m%d_%H%M")

    if bool(CarolConfig):
        # create log file name
        LogName = (LOG_LocalPath + "charon-" + date_time + "-" + C_constraint + "_" + str(C_vals[i]) + 
            C_units + "-"+ "iter_" + str(ipsec_N) + ".log")
    else:
        LogName = ("./charon-" + date_time + "baseline_" + str(C_vals[i]) + "-iter_" + str(ipsec_N) + ".log")
    
    # Copy log file from Carol to local machine
    docker.copy(("carol", RemotePath), LogName)

    #Reload Settings which forces a new Charon Log File
    docker.execute("carol", shlex.split("echo 'newlog' > /var/log/charon.log"))
    docker.execute("carol", shlex.split("swanctl --reload-settings"))

    #print run stats and estimated remaining time
    total_time = time.perf_counter() - startrun_tic
    L1_time = time.perf_counter() - L1_tic
    EstRemTime = (len(C_vals)-i) * L1_time
    if pLvl > 1:
        print("Total Time: " + str(total_time) + " seconds")
        print("Last Run Time: " + str(L1_time) + " seconds")
        print("Estimated Remaining Time: " + str(EstRemTime) + " seconds")

    #save run stats to file
    file1 = open((LOG_LocalPath + "runstats.txt"),"a")
    file1.writelines(LogName + "; " +
        "Additional Params: " + C_AddParams + "; tc_command: " + tc_string +
        "; IterationTime: " + str(L1_time) + " seconds" + 
        "; Total Run Time: " + str(total_time) + " seconds\n")
    file1.close()

    #check timer if > max time break loop
    if time.perf_counter() - startrun_tic > max_run_time:
        break

#END Constraint 1 Loop

# If not done previously Move all Data Files from Carol to local machine

if pLvl > 0:
    print(" -- Wrapping Up Run -- ")

#print run stats
total_time = time.perf_counter() - startrun_tic
if pLvl > 1:
    print("Total Time: " + str(total_time) + " seconds")



#remove all TC constraints
try:
    docker.execute("carol", shlex.split("tc qdisc del dev eth0 root"))
    docker.execute("moon", shlex.split("tc qdisc del dev eth0 root"))
except:
    if pLvl > 1:
        print("Possible Error removing TC constraints")

## Stop Docker Containers
docker.compose.down()
