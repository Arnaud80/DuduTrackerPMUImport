#!/usr/local/bin/python3

"""
TODO :
    Gérer les exeptions à l'ouverture des fichier (ex. .DS_Store) 
"""

import requests
import json
#import time
import logging
import os
import re
import datetime as dt

"""
    Import config file
"""
import config
PMULogFolder=config.PMULogFolder
mainPlayer=config.mainPlayer


logging.info("DuduTrackerPMUImport is started ...")
    
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
        
        """
        try:                    
            file = open(PMULogFile , "r", encoding='utf8')
        except:
            print("Could not read file :" + f)
        with file :
            try :  
                lines=file.readlines()
            except:
                print("Could not read lines in file :" + f)
                break
            with lines:
        """
        nbLines=len(lines)-1
        
        def inc_n(n, max_n):
            if n < max_n :
                return n+1
            else :
                return n
           
        for n in range(0,len(lines)):
            game_num=""
            gameType=""
            TimeStamp=""
            table_name=""
            button_pos=""
            nbPlayer=""
            maxPlayer=""
            flop=""
            turn=""
            river=""
            handPlayers={mainPlayer:""}
            
            # Récupère le n° du jeu
            pattern = re.compile("#Game No : ") # Construit la pattern recherché
            match = pattern.search(lines[n]) # Recherche la pattern
            if match:
                game_num=lines[n][match.end():-1]
                #print("Game n° : " + game_num) # Affiche la fin de ligne contenant la pattern. -1 pour ne pas prendre le dernier caractère "\n"
                n=inc_n(n, nbLines)
                if n==nbLines : break
                pattern = re.compile("Hand History for Game") # Construit la pattern recherché
                match = pattern.search(lines[n]) # Recherche la pattern
                if match:
                    # Récupère le type de jeu et le date
                    n=inc_n(n, nbLines)
                    if n==nbLines : break
                    gameType=re.split(" - ",lines[n])[0]
                    gameType=re.sub("'", "\\'", gameType)
                    
                    dateTimeStr=re.split(" - ",lines[n])[1][0:-1]
                    dateTimeObj=dt.datetime.strptime(dateTimeStr,"%A,%B %d, %H:%M:%S %Z %Y")
                    #print("GameType : " + gameType)
                    TimeStamp=dateTimeObj
                    #print("Timestamp : " + TimeStamp)
                    
                    # Récupère le nom de la table
                    n=inc_n(n, nbLines)
                    if n==nbLines : break
                    pattern = re.compile("Table ") # Construit la pattern recherché
                    match = pattern.search(lines[n]) # Recherche la pattern
                    table_name=lines[n][match.end():][0:-1]
                    table_name=re.sub("'", "\\'", table_name)
                    #print("Table name : " + table_name)
                    
                    # Récupère la position du bouton
                    n=inc_n(n, nbLines)
                    if n==nbLines : break
                    pattern = re.compile("Seat ") # Construit la pattern recherché
                    match = pattern.search(lines[n]) # Recherche la pattern
                    button_pos=lines[n][match.end():][0]
                    #print("Position bouton : " + button_pos)
        
                    # Récupère le nombre de joueur à la table
                    n=inc_n(n, nbLines)
                    if n==nbLines : break
                    pattern = re.compile("Total number of players : ") # Construit la pattern recherché
                    match = pattern.search(lines[n]) # Recherche la pattern
                    QtyPlayer=re.split("/",lines[n][match.end():])
                    nbPlayer=QtyPlayer[0]
                    maxPlayer=QtyPlayer[1][0:-1]
                    #print("QtyPlayer : " + nbPlayer)
                    #print("PlayerMax : " + maxPlayer)
                    
                    # Récupère le nom des joueurs à la table
                    for i in range(0,int(QtyPlayer[0])):
                        n=inc_n(n, nbLines)
                        if n==nbLines : break
                        pattern = re.compile("seat ") # Construit la pattern recherché
                        match = pattern.search(lines[n]) # Recherche la pattern
                        playerName = re.split("\(",lines[n][match.end():])[0][3:-1]
                        playerName=re.sub("'", "\\'", playerName)
                        handPlayers[playerName]=""
                        #print("Player : " + playerName)
                        
                    # On passe les lignes jusque ** Dealing down cards **
                    inc_n(n, nbLines)
                    while (lines[n][0:-1]!="** Dealing down cards **"):
                        n=inc_n(n, nbLines)
                        if n==nbLines : break
                        
                    # On récupère la main du joueur
                    n=inc_n(n, nbLines)
                    if n==nbLines : break
                    pattern = re.compile("\[") # Construit la pattern recherché
                    match = pattern.search(lines[n]) # Recherche la pattern
                    Hand = re.split(",",lines[n][match.end():-2])
                    mainHand=Hand[0][1:] + "," + Hand[1][1:-1]
                    handPlayers[mainPlayer]=mainHand
                    #print("Hand : " + mainHand)            
                    
                    # On passe les lignes jusque ** Dealing Flop ** ou #Game No
                    while (n<nbLines):
                        n=inc_n(n, nbLines)
                        #if n==nbLines : break
                        match = re.match("^\*\* Dealing Flop \*\*|^#Game No", lines[n]) # recherche la pattern
                        if match:
                            if match[0]=="** Dealing Flop **":
                                flop=lines[n][21:-3]
                                flop=re.sub(" ","",flop)
                                #print("Flop : " + flop)
                                #n-=1
                            break            
                    
                    # On passe les lignes jusque ** Dealing Turn ** ou #Game No
                    while (n<nbLines):
                        n=inc_n(n, nbLines)
                        #if n==nbLines : break
                        match = re.match("^\*\* Dealing Turn \*\*|^#Game No", lines[n]) # recherche la pattern
                        if match:
                            if match[0]=="** Dealing Turn **":
                                turn=lines[n][21:-3]
                                #print("Turn : " + turn)
                                #n-=1
                            break
                        
                    if n==nbLines :
                        #print("Fin du fichier !")
                        break
                        
                    # On passe les lignes jusque ** Dealing River ** ou #Game No
                    if match[0]!="#Game No" :    
                        while (n<nbLines):
                            n=inc_n(n, nbLines)
                            #if n==nbLines : break
                            match = re.match("^\*\* Dealing River \*\*|^#Game No", lines[n]) # recherche la pattern
                            if match:
                                if match[0]=="** Dealing River **":
                                    river=lines[n][22:-3]
                                    #print("River : " + river)
                                break
                            
                    if n==nbLines :
                        #print("Fin du fichier !")
                        break
                            
                    # On passe les lignes jusque *shows [ ou #Game No
                    if match[0]!="#Game No" :
                        while (n<nbLines):
                            n=inc_n(n, nbLines)
                            #if n==nbLines : break
                            match = re.search("shows|doesn't show|^#Game No", lines[n]) # recherche la pattern
                            if match:
                                if match[0]=="#Game No":
                                    break
                                if match[0]=="shows":
                                    shows_line=lines[n].split(" ")
                                    handPlayerName=shows_line[0]
                                    handPlayerName=re.sub("'", "\\'", handPlayerName)
                                    handPlayer=shows_line[3] + shows_line[4]
                                    handPlayers[handPlayerName]=handPlayer
                                    
                                    #print("Hand Player name :" + handPlayerName)
                                    #print("Hand :" + handPlayers[handPlayerName])
                                    
                                    
                                if match[0]=="doesn't show" :
                                    shows_line=lines[n].split(" ")
                                    handPlayerName=shows_line[0]
                                    handPlayerName=re.sub("'", "\\'", handPlayerName)
                                    handPlayer=shows_line[4] + shows_line[5]
                                    handPlayers[handPlayerName]=handPlayer
                                    
                                    #print("Hand Player name :" + handPlayerName)
                                    #print("Hand :" + handPlayers[handPlayerName])
                                    
                    #print("Game n° : " + game_num) # Affiche la fin de ligne contenant la pattern. -1 pour ne pas prendre le dernier caractère "\n"
                    #print("GameType : " + gameType)
                    #print("Timestamp : " + TimeStamp)
                    #print("Table name : " + table_name)
                    #print("Position bouton : " + button_pos)
                    #print("QtyPlayer : " + nbPlayer)
                    #print("PlayerMax : " + maxPlayer)
                    #print("Flop :" + flop)
                    #print("Turn : " + turn)
                    #print("River : " + river)
                    #print("handPlayers" + handPlayers.__str__())
                    
                    api_url="http://localhost:8080/hands"
                    data = {
                        'game_num':game_num,
                        'gameType':gameType,
                        'TimeStamp':TimeStamp,
                        'table_name':table_name,
                        'button_pos':button_pos,
                        'nbPlayer':nbPlayer,
                        'maxPlayer':maxPlayer,
                        'flop':flop,
                        'turn':turn,
                        'river':river,
                        'handPlayers':json.dumps(handPlayers,ensure_ascii=False)}
                
                    result=requests.post(api_url, data)
                    obj=json.loads(result.content)
                    print(obj)
                    #break;
                    
        file.close()