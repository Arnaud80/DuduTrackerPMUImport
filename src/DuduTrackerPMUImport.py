#!/usr/local/bin/python3

import os
from myLogger import logger
from pmu import recordHands
import argparse
import config
from config import mainPlayer


parser = argparse.ArgumentParser()
parser.add_argument("-PMULogFolder", default=config.PMULogFolder)
args = parser.parse_args()


PMULogFolder = args.PMULogFolder     

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