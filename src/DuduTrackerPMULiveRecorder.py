#!/usr/local/bin/python3
from time import strftime, localtime, sleep
from pmu import recordHands
import os
from config import PMULogFolder, mainPlayer
from myLogger import logger
from multiprocessing import Process

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
    

def parseFile(PMULogFile):
    pos=0
    while True:
        result = readLines(PMULogFile, pos)
        lines=result[0]
        pos=result[1]
        
        recordHands(lines, mainPlayer, PMULogFile)

# Read PMU Log files
# Boucle sur les files du dossier de Log PMU du jour
r=PMULogFolder + "/" + currentFolder
TargetFileList=list()

while True:
    fileList=os.listdir(r)
    for file in fileList:
        if file not in TargetFileList:
            TargetFileList.append(file)
            PMULogFile=os.path.join(r, file)
            logger.warning("Import of " + PMULogFile)
                    
            if __name__ == '__main__':
                p = Process(target=parseFile, args=(PMULogFile,))
                p.start()
    sleep(3)
