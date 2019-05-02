#!/usr/local/bin/python3

"""
TODO :
    Gérer les exeptions à l'ouverture des fichier (ex. .DS_Store) 
"""

import os
from myLogger import logger
from pmu import recordHands

"""
    Import config file
"""
import config
PMULogFolder=config.PMULogFolder
mainPlayer=config.mainPlayer


logger.info("DuduTrackerPMUImport is started ...")
    
#Read PMU Log files
# Boucle sur les folder et files du dossier de Log PMU
# r=root, d=directories, f = files
for r, d, f in os.walk(PMULogFolder):
    for file in f:
        #print(os.path.join(r, file))
        PMULogFile=os.path.join(r, file)
        print("Import of " + PMULogFile)
        
        file = open(PMULogFile , "r", encoding='utf8')
        lines=file.readlines()

        recordHands(lines, mainPlayer)