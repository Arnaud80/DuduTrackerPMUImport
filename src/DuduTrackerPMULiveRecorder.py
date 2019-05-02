#!/usr/local/bin/python3

"""
"""

from time import strftime, localtime, sleep
from pmu import recordHands
import os
from config import PMULogFolder, mainPlayer
from myLogger import logger


currentFolder=strftime("%Y%m%d", localtime())


logger.warning("DuduTrackerPMULiveRecorder is started ...")
logger.info("CurrentFolder : " + currentFolder)

def readLines(file, pos):
    file = open(file , "r", encoding='utf8')
    file.seek(pos)
    lines=file.readlines()
    pos=file.tell()
    file.close()
    sleep(1)
    return(lines, pos)
    
# Read PMU Log files
# Boucle sur les files du dossier de Log PMU du jour
# r=root, d=directories, f = files
for r, d, f in os.walk(PMULogFolder + "/" + currentFolder):
    for file in f:
        PMULogFile=os.path.join(r, file)
        logLines=[]
        pos=0
        logger.warning("Import of " + PMULogFile)
                
        while True:
            result = readLines(PMULogFile, pos)
            lines=result[0]
            pos=result[1]
            
            recordHands(lines, mainPlayer)
