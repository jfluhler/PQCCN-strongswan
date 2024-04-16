# Data-Collection

**Core Data Collection Script**

  This script is the core data collection script for the PostQuantumIKEv2 project.
  The script is designed to be run on a host machine and will interact with Docker to start and stop containers.
  The script will also interact with the containers to enable qdisc for tc, and to start strongswan the charon daemon.
  The script then invokes a loop to change the tc constraints an inner loop then initiates and terminates
  the IPSEC connection a defined number of times. Once the IPSEC loop is complete the script will update the tc
  constraints and repeat the process. Once the tc constraint range has been covered, script will copy the charon
  log files from the Carol container to the host machine. The script will also log the run stats to a file.
  Finally, the script will also remove all qdisc constraints and stop the containers.

To run the script, the user must provide a YAML configuration file. This can be passed to python as an argument
  in the terminal or the default file will be used. The default file is ```DataCollect_baseline.yaml``` but this
  can be changed in the code below.

Example terminal command:
```Bash
cd PQCCN-strongswan/data-collection/
python3 DataCollectCore.py config/DataCollect_baseline.yaml
```

**DataCollectCore.py Flowchart**
- Blocks in orange indicate use of user configured parameters.
- Blocks in blue indicate use of calculated parameters
- Blocks in gray indicate missing features.

![DataCollectionSoftwareDiagram.png](DataCollectionSoftwareDiagram.png){border-effect=line}


## Config files
The DataCollectCore.py script expects to be passed a configuration file when called. 
The configuration files use a yaml format. The config files has three distinct parts:

- CoreConfig: These are the user parameters that control the core elements of the script.
- Carol_TC_Config: These are the constraints to be applied to "Carol" with the first constraint being the one which is adjusted.
- Moon_TC_Config: These are the constraints to be applied to "Moon" note however these are not adjusted.

> If you want a matching and adjusted / variable constraint on Carol and Moon, 
> set the MirrorMoon: true in the CoreConfig. 
> {style="note"}

### Example Config Files:
<tabs>
    <tab title="Delay Example">
        <code-block lang="yaml">
            ---
            CoreConfig:           # Core configuration settings for the run.
              TC_Iterations: 10  # Number of times to form and tear-down the IPsec tunnel, per TC setting.
              MaxTimeS: 36000      # Maximum time to run the test in seconds.
              LocalPath: "~/PQCCN_LOGS/"      # Local path to copy the logs to.
              RemotePath: "/var/log/charon.log"   # Remote path to copy the log file from.
              WiresharkLogs: false        # Capture Wireshark logs from Carol. 
              WSRemotePath: "/var/log/"   # Remote path to copy the Wireshark logs from.
              WSLocalPath: "/"            # Local path to copy the Wireshark logs to.
              MirrorMoon: false           # Do not Mirror the Carol's TC settings to Moon.
              PrintLevel: 1               # Information Display Level for the run.
              compose_files: "~/PQCCN-strongswan/pq-strongswan/docker-compose.yml"  # Docker compose file location
            Carol_TC_Config:    # Carol's Traffic Control settings.
              Constraint1:      # Constraint 1, this is the adjustable constraint.
                Type: netem     # Type of constraint, netem for network emulation.
                Constraint: delay  # Constraint to adjust, delay in this case.  
                Interface: eth0    # Interface to apply the constraint to.
                StartRange: 1      # Start range of the constraint (1ms).
                EndRange: 200      # End range of the constraint (200ms).
                Units: ms          # Units of the constraint (milliseconds).
                Steps: 5           # Number of steps to take between the start and end range.
                AddParams: ''      # Additional parameters to add to the constraint.</code-block>
    </tab>
    <tab title="Loss Example">
        <code-block lang="yaml">
            ---
            CoreConfig:           # Core configuration settings for the run.
              TC_Iterations: 10  # Number of times to form and tear-down the IPsec tunnel, per TC setting.
              MaxTimeS: 36000      # Maximum time to run the test in seconds.
              LocalPath: "~/PQCCN_LOGS/"      # Local path to copy the logs to.
              RemotePath: "/var/log/charon.log"   # Remote path to copy the log file from.
              WiresharkLogs: false        # Capture Wireshark logs from Carol. 
              WSRemotePath: "/var/log/"   # Remote path to copy the Wireshark logs from.
              WSLocalPath: "/"            # Local path to copy the Wireshark logs to.
              MirrorMoon: false           # Do not Mirror the Carol's TC settings to Moon.
              PrintLevel: 1               # Information Display Level for the run.
              compose_files: "~/PQCCN-strongswan/pq-strongswan/docker-compose.yml"  # Docker compose file location
            Carol_TC_Config:
              Constraint1:
                Type: netem
                Constraint: loss
                Interface: eth0
                StartRange: 0.1
                EndRange: 25
                Units: "%"
                Steps: 5
                AddParams: ''</code-block>
    </tab>
    <tab title="Bandwidth Example Windows">
            <code-block lang="yaml">
                ---
                CoreConfig:           # Core configuration settings for the run.
                  TC_Iterations: 10  # Number of times to form and tear-down the IPsec tunnel, per TC setting.
                  MaxTimeS: 72000      # Maximum time to run the test in seconds.
                  LocalPath: 'C:\PQCCN_LOGS\'      # Local path to copy the logs to.
                  RemotePath: '/var/log/charon.log'   # Remote path to copy the log file from.
                  WiresharkLogs: false        # Capture Wireshark logs from Carol. 
                  WSRemotePath: '/var/log/'   # Remote path to copy the Wireshark logs from.
                  WSLocalPath: "/"            # Local path to copy the Wireshark logs to.
                  MirrorMoon: false           # Do not Mirror the Carol's TC settings to Moon.
                  PrintLevel: 2               # Information Display Level for the run.
                  compose_files: 'C:\GitHub\PQCCN-strongswan\pq-strongswan\docker-compose.yml'  # Docker compose file location
                Carol_TC_Config:  # Carol's Traffic Control settings.
                  Constraint1:      # Constraint 1, this is the adjustable constraint.
                    Type: tbf           # Type of constraint, tbf for token bucket filter.
                    Constraint: rate    # Constraint to adjust, rate in this case.
                    Interface: eth0     # Interface to apply the constraint to.
                    StartRange: 11    # Start range of the constraint.
                    EndRange: 1        # End range of the constraint.
                    Units: kbit         # Units of the constraint.
                    Steps: 11           # Number of steps to take between the start and end range.
                    AddParams: burst 301kbit latency 250ms     # Additional parameters to add to the constraint.</code-block>
    </tab>
    <tab title="Carol and Moon Constraints Example">
        <code-block lang="yaml">
                ---
                CoreConfig:           # Core configuration settings for the run.
                  TC_Iterations: 10  # Number of times to form and tear-down the IPsec tunnel, per TC setting.
                  MaxTimeS: 36000      # Maximum time to run the test in seconds.
                  LocalPath: "../"      # Local path to copy the logs to.
                  RemotePath: "/var/log/charon.log"   # Remote path to copy the log file from.
                  WiresharkLogs: false        # Capture Wireshark logs from Carol. 
                  WSRemotePath: "/var/log/"   # Remote path to copy the Wireshark logs from.
                  WSLocalPath: "/"            # Local path to copy the Wireshark logs to.
                  MirrorMoon: false           # Do not Mirror the Carol's TC settings to Moon.
                  PrintLevel: 1               # Information Display Level for the run.
                  compose_files: "./pq-strongswan/docker-compose.yml"  # Docker compose file location
                Carol_TC_Config:  # Carol's Traffic Control settings.
                  Constraint1:        # Constraint 1, this is the adjustable constraint.
                    Type: netem         # Type of constraint, netem for network emulation.
                    Constraint: delay   # Constraint to adjust, delay in this case.
                    Interface: eth0     # Interface to apply the constraint to.
                    StartRange: 1       # Start range of the constraint.
                    EndRange: 200       # End range of the constraint.
                    Units: ms           # Units of the constraint.
                    Steps: 2            # Number of steps to take between the start and end range.
                    AddParams: ''       # Additional parameters to add to the constraint. EG: 'loss 0.1%'
                  Constraint2:    # Constraint 2, this NOT adjustable. 
                    Type: netem   # IF the type matches Constraint 1, it will be placed in AddParams for constraint 1.
                    Constraint: loss    # Constraint to add, loss in this case
                    Interface: eth0     # Interface to apply the constraint to.
                    StartRange: 0.1     # Value to set for the constraint.
                    Units: "%"          # Units of the constraint, percentage in this case.
                    Steps: 1            # This is ignored as "additional" constraints are not adjustable.
                    AddParams: ''       # Additional parameters to add to the constraint. EG: 'delay 100ms'
                Moon_TC_Config:   # Moon's Traffic Control settings.
                  Constraint1:        # Constraint 1, this is not an adjustable constraint.
                    Type: netem
                    Constraint: delay
                    Interface: eth0
                    StartRange: 1
                    EndRange: 1000
                    Units: ms
                    Steps: 1
                    AddParams: ''</code-block>
    </tab>
</tabs>




