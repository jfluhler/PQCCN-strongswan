# PQCCN-strongswan
pq-strongswan wrapper for data collection and analysis. Advancing IKEv2 for the Quantum Age: Challenges in Post-Quantum Cryptography Implementation on Constrained Network

For full documentation refer to the <a target="_blank" rel="noreferrer noopener" href="https://jfluhler.github.io/PQCCN-strongswan/">Project Github Pages</a>

# Quick Setup Guide

The data-collection part of this project operates like a wrapper to the
[strongX509/pq-strongswan](https://github.com/strongX509/docker/tree/master/pq-strongswan">strongX509/pq-strongswan)
docker container. However, there are some modification from the pq-strongswan base repository. 
We want to specially note that the work by [Andreas Steffen](https://github.com/strongX509) in making the pq-strongswan repo was of great help in starting this project. The core of efforts are at the core of this project.

## Before you start

The following pre-requisites that are required to use this project.
- Docker
- Python 3

## Setup

Let's walk through building the docker container and installing required python modules.

1. Open a terminal console
2. Locate docker composer file
   Navigate to the folder with the docker configuration file: docker-compose.yml
   Generally the path may look like ```~/strongX509/pq-strongswan/docker-compose.yml```
   If you are using our included fork of pq-strongswan the path will simply be
   ```PQCCN-strongswan/pq-stronswan```

3. Build the container
   ```bash
   docker build .
   ```
   Wait for the process to complete, it could take some time if your internet connection is slow

4. Validate the container launches
   In a terminal window / console 
   ```bash
   docker compose up
   ```
   > Docker and sudo
   > 
   > ```sudo``` should not be required to run most docker commands like docker compose up. 
   > If this operation fails without sudo, you need to fix your system permissions for docker.
   > {style="note"}

5. Install required python libraries

   - numpy
   - pyyaml
   - docker_on_whales
   - tqdm
   
   ```bash
   pip install numpy, docker_on_whales, pyyaml, tqdm
   ```

   > If you are using a virtual env for python. be certain to enter that environment before installing modules.
   
***You did it! The required resources are now installed!***


License: <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>
