#!/usr/local/bin/python3
import requests
import json
import re
import datetime as dt
from myLogger import logger

def inc_n(n, max_n):
    if n < max_n :
        return n+1
    else :
        return n

def recordHands(lines, mainPlayer):
    nbLines=len(lines)-1
    logger.debug("nbLines : " + str(nbLines))
    
    for n in range(0,len(lines)):
        #Initialization of needed variables
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
        handPlayers={}
        
        # Loop until the line "#Game No : "
        pattern = re.compile("#Game No : ") # Searched pattern
        match = pattern.search(lines[n]) # Search the pattern in the current line
        if match:
            game_num=lines[n][match.end():-1] #Get the string from the end of the patterne until the end of the line
            logger.debug("game_num : " + game_num)
            n=inc_n(n, nbLines) # Go directly to the next line (we don't wait the loop of for insctruction
            if n==nbLines : break
            
            #Loop until the line "Hand History for Game"
            pattern = re.compile("Hand History for Game") 
            match = pattern.search(lines[n])
            if match:
                # Get the type and the date of the game
                n=inc_n(n, nbLines) # The searched line is just under the line "Hand History for Game", whith this structure Type_game - Date and hour
                if n==nbLines : break
                gameType=re.split(" - ",lines[n])[0]
                gameType=re.sub("'", "\\'", gameType) # We escape (\') the eventual ' carracters
                logger.debug("gameType : " + gameType)
                
                dateTimeStr=re.split(" - ",lines[n])[1][0:-1]
                dateTimeObj=dt.datetime.strptime(dateTimeStr,"%A,%B %d, %H:%M:%S %Z %Y")
                TimeStamp=dateTimeObj
                logger.debug("TimeStamp : " + str(TimeStamp))
                
                # Get the Table name
                n=inc_n(n, nbLines) # Go directly to the next line
                if n==nbLines : break
                pattern = re.compile("Table ")
                match = pattern.search(lines[n])
                table_name=lines[n][match.end():][0:-1]
                table_name=re.sub("'", "\\'", table_name)
                logger.debug("table_name : " + table_name)
                
                # Get the button position
                n=inc_n(n, nbLines) # Go directly to the next line
                if n==nbLines : break
                pattern = re.compile("Seat ") # Construit la pattern recherché
                match = pattern.search(lines[n]) # Recherche la pattern
                button_pos=lines[n][match.end():][0]
                logger.debug("button_pos : " + button_pos)
    
                # Get the number of player on the table
                n=inc_n(n, nbLines)
                if n==nbLines : break
                pattern = re.compile("Total number of players : ") # Construit la pattern recherché
                match = pattern.search(lines[n]) # Recherche la pattern
                QtyPlayer=re.split("/",lines[n][match.end():])
                nbPlayer=QtyPlayer[0]
                maxPlayer=QtyPlayer[1][0:-1]
                logger.debug("nbPlayer : " + nbPlayer)
                logger.debug("maxPlayer : " + maxPlayer)
                
                # Get players name
                #for i in range(0,int(QtyPlayer[0])):
                #    n=inc_n(n, nbLines)
                #    if n==nbLines : break
                #    pattern = re.compile("seat ") # Construit la pattern recherché
                #    match = pattern.search(lines[n]) # Recherche la pattern
                #    playerName = re.split("\(",lines[n][match.end():])[0][3:-1]
                #    playerName=re.sub("'", "\\'", playerName)
                #    handPlayers[playerName]="" # Initialize the variable to catch the player hand
                #    logger.debug("playerName : " + playerName)
                    
                # skip lines until ** Dealing down cards **
                inc_n(n, nbLines)
                while (lines[n][0:-1]!="** Dealing down cards **"):
                    n=inc_n(n, nbLines)
                    if n==nbLines : break
                    
                # Get main player hand
                n=inc_n(n, nbLines)
                if n==nbLines : break
                pattern = re.compile("\[")
                match = pattern.search(lines[n])
                Hand = re.split(",",lines[n][match.end():-2])
                mainHand=Hand[0][1:] + "," + Hand[1][1:-1]
                handPlayers[mainPlayer]=mainHand
                logger.debug("handPlayers[" + mainPlayer + "] : " + handPlayers[mainPlayer])            
                
                # Skip lines until ** Dealing Flop ** or #Game No
                while (n<nbLines):
                    n=inc_n(n, nbLines)
                    #if n==nbLines : break # Todo : Check why this line is commented
                    match = re.match("^\*\* Dealing Flop \*\*|^#Game No", lines[n])
                    if match:
                        if match[0]=="** Dealing Flop **":
                            flop=lines[n][21:-3]
                            flop=re.sub(" ","",flop)
                            logger.debug("flop : " + flop)
                            
                            # Skip lines until ** Dealing Turn ** or #Game No
                            while (n<nbLines):
                                n=inc_n(n, nbLines)
                                #if n==nbLines : break # Todo : Check why this line is commented
                                match = re.match("^\*\* Dealing Turn \*\*|^#Game No", lines[n])
                                if match:
                                    if match[0]=="** Dealing Turn **":
                                        turn=lines[n][21:-3]
                                        logger.debug("turn : " + turn)
                                        
                                        # skip lines until ** Dealing River ** or #Game No
                                        while (n<nbLines):
                                            n=inc_n(n, nbLines)
                                            #if n==nbLines : break # Todo : Check why this line is commented
                                            match = re.match("^\*\* Dealing River \*\*|^#Game No", lines[n])
                                            if match:
                                                if match[0]=="** Dealing River **":
                                                    river=lines[n][22:-3]
                                                    logger.debug("turn : " + turn)
                                                    
                                                    # skip lines until shows or doesn't show or #Game No
                                                    while (n<nbLines):
                                                        n=inc_n(n, nbLines)
                                                        #if n==nbLines : break # Todo : Check why this line is commented
                                                        match = re.search("shows|doesn't show|^#Game No", lines[n])
                                                        if match:
                                                            if match[0]=="#Game No":
                                                                break
                                                            
                                                            if (match[0]=="shows") :
                                                                shows_line=lines[n].split(" ")
                                                                handPlayerName=shows_line[0];
                                                                show_pos=1;
                                                                while shows_line[show_pos]!="shows" :
                                                                    handPlayerName=handPlayerName+" "+shows_line[show_pos]
                                                                    show_pos+=1;
                                                                    
                                                                handPlayerName=re.sub("'", "\\'", handPlayerName)
                                                                handPlayer=shows_line[show_pos+2] + shows_line[show_pos+3]
                                                                handPlayers[handPlayerName]=handPlayer
                                                                logger.debug("handPlayers[" + handPlayerName + "] : " + handPlayers[handPlayerName])
                                                                
                                                            if match[0]=="doesn't show" :
                                                                shows_line=lines[n].split(" ")
                                                                handPlayerName=shows_line[0];
                                                                show_pos=1;
                                                                while shows_line[show_pos]!="doesn't":
                                                                    handPlayerName=handPlayerName+" "+shows_line[show_pos]
                                                                    show_pos+=1;
                                                                
                                                                handPlayerName=re.sub("'", "\\'", handPlayerName)
                                                                handPlayer=shows_line[show_pos+3] + shows_line[show_pos+4]
                                                                handPlayers[handPlayerName]=handPlayer
                                                                logger.debug("handPlayers[" + handPlayerName + "] : " + handPlayers[handPlayerName])
                                                # if the match = #Game No or endfile
                                                break
                                    # if the match = #Game No or endfile
                                    break
                        # if the match = #Game No or endfile
                        break            
                                                    
                # Call API to record the hand
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
                logger.debug("data : " + str(data))
            
                result=requests.post(api_url, data)
                obj=json.loads(result.content)
                logger.debug("API hand record result : " + str(obj))
                
                # Todo : Check why this test is here, seem not useful !
                if n==nbLines :
                    logger.debug("End of file")
                    break