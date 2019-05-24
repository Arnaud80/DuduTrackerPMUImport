#!/usr/local/bin/python3
import requests
import json
import re
import datetime as dt
from myLogger import logger
from decimal import Decimal
from config import api_url

# Function to increment number only if value is min to max value
def inc_n(n, max_n):
    if n < max_n :
        return n+1
    else :
        return n

# Function to get winners
# Return the list of winners and the last line numbers of winners
def getWinners(winners, lines, n, nbLines):
    res={}
    n=n-1
    while (n<nbLines):
        n=inc_n(n, nbLines)
        if n==nbLines : break
        pattern = re.compile(r"wins") # Construct the pattern
        match = pattern.search(lines[n]) # Search the pattern
        if match is None :
            break
        else:
            playerName = lines[n][0:match.start()-1]
            playerName = re.sub("'", "\\'", playerName)
            pattern = re.compile(r"side") # Construct the pattern
            lines[n]=lines[n].replace(",","")
            match = pattern.search(lines[n]) # Search the pattern
            
            match_amount = re.findall(r"(\d+(\.\d+)?)", lines[n]) # Search all numbers
            
            if match :
                amount=float(match_amount[len(match_amount)-2][0])
                if playerName in winners.keys() :
                    winners[playerName]=(winners[playerName]*100+amount*100)/100
                else :
                    winners[playerName]=amount
            else :                                                        
                amount=float(match_amount[len(match_amount)-1][0])
                if playerName in winners.keys() :
                    winners[playerName]=(winners[playerName]*100+amount*100)/100
                else :
                    winners[playerName]=amount
            logger.debug("winners[" + playerName + "]: " + str(winners[playerName]))
    res["n"]=n
    res["winners"]=winners
    return res

def recordHands(lines, mainPlayer):
    nbLines=len(lines)-1
    if nbLines<0 :
        logger.debug("wait for new lines ...")
    else :
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
        players=[]
        preflop_actions={}
        flop_actions={}
        turn_actions={}
        river_actions={}
        handPlayers={}
        smallBlindPlayer=""
        smallBlind=""
        bigBlindPlayer=""
        bigBlind=""
        winners={}
        
        # Loop until the line "#Game No : "
        pattern = re.compile("#Game No : ") # Searched pattern
        match = pattern.search(lines[n]) # Search the pattern in the current line
        if match:
            game_num=lines[n][match.end():-1] #Get the string from the end of the patterne until the end of the line
            logger.debug("game_num : " + game_num)
            n=inc_n(n, nbLines) # Go directly to the next line (we don't wait the loop for insctruction
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
                pattern = re.compile("Seat ") # Construct the pattern
                match = pattern.search(lines[n]) # Search the pattern
                button_pos=lines[n][match.end():][0]
                logger.debug("button_pos : " + button_pos)
    
                # Get the number of player on the table
                n=inc_n(n, nbLines)
                if n==nbLines : break
                pattern = re.compile("Total number of players : ") # Construct the pattern
                match = pattern.search(lines[n]) # Search the pattern
                QtyPlayer=re.split("/",lines[n][match.end():])
                nbPlayer=QtyPlayer[0]
                maxPlayer=QtyPlayer[1][0:-1]
                logger.debug("nbPlayer : " + nbPlayer)
                logger.debug("maxPlayer : " + maxPlayer)
                
                # Get players name
                for i in range(0,int(QtyPlayer[0])):
                    n=inc_n(n, nbLines)
                    if n==nbLines : break
                    pattern = re.compile("seat ") # Construct the pattern
                    match = pattern.search(lines[n]) # Search pattern
                    playerName = re.split(r"\(",lines[n][match.end():])[0][3:-1]
                    playerName=re.sub("'", "\\'", playerName)
                    players.append(playerName)
                    logger.debug("players[" + str(i) + "] : " + playerName)
                
                # Get Small blind
                # skip lines until small blind
                while (n<nbLines):
                    n=inc_n(n, nbLines)
                    if n==nbLines : break
                    pattern = re.compile(r"small blind|no Small Blind") # Construct the pattern
                    match = pattern.search(lines[n]) # Search the pattern
                    if match:
                        if match[0]=="small blind" :
                            match = re.findall(r"(\d+(\.\d+)?)", lines[n]) # Construct the pattern
                            smallBlind = match[len(match)-1][0]
                            match = re.search(" posts",lines[n]) # Search the pattern
                            smallBlindPlayer = lines[n][0:match.start()]
                            logger.debug("smallBlind : " + smallBlind)
                            logger.debug("smallBlindPlayer : " + smallBlindPlayer)
                    break

                # Get Big blind
                # skip lines until small blind
                while (n<nbLines):
                    n=inc_n(n, nbLines)
                    if n==nbLines : break
                    pattern = re.compile(r"big blind") # Construct the pattern
                    match = pattern.search(lines[n]) # Search the pattern
                    if match:
                        match = re.findall(r"(\d+(\.\d+)?)", lines[n]) # Construct the pattern
                        bigBlind = match[len(match)-1][0]
                        match = re.search(" posts",lines[n]) # Search the pattern
                        bigBlindPlayer = lines[n][0:match.start()]
                        logger.debug("bigBlind : " + bigBlind)
                        logger.debug("bigBlindPlayer : " + bigBlindPlayer)
                        break

                # skip lines until ** Dealing down cards **
                inc_n(n, nbLines)
                while (lines[n][0:-1]!="** Dealing down cards **"):
                    n=inc_n(n, nbLines)
                    if n==nbLines : break
                    
                # Get main player hand
                n=inc_n(n, nbLines)
                if n==nbLines : break
                pattern = re.compile(r"\[")
                match = pattern.search(lines[n])
                Hand = re.split(",",lines[n][match.end():-2])
                mainHand=Hand[0][1:] + "," + Hand[1][1:-1]
                handPlayers[mainPlayer]=mainHand
                logger.debug("handPlayers[" + mainPlayer + "] : " + handPlayers[mainPlayer])    

                # Get preflop actions
                while (n<nbLines):
                    n=inc_n(n, nbLines)
                    if n==nbLines : break
                    #pattern = re.compile(r"all-In|raises|bets|calls|folds|Folds|checks|time|break|moved|disconnected|reconnected|Chat|^\*\* Dealing Flop \*\*|^#Game No|does") # Construct the pattern
                    #pattern = re.compile(r"all-In|raises|bets|calls|folds|Folds|checks|^\*\* Dealing Flop \*\*|^#Game No|does") # Construct the pattern
                    pattern = re.compile(r"^\*\* Dealing Flop \*\*|^#Game No|does") # Construct the pattern
                    match_action = pattern.search(lines[n]) # Search the pattern
                    if match_action :
                        n=n-1
                        break
                    else :
                        #pattern = re.compile("all-In|raises|bets|calls|folds|Folds|checks") # Construct the pattern
                        pattern = re.compile("all-In|raises|bets|calls|folds|Folds|checks") # Construct the pattern
                        match_action = pattern.search(lines[n]) # Search the pattern
                        if match_action : #!='time' and match_action[0]!='break' and match_action[0]!='moved' and match_action[0]!='disconnected' and match_action[0]!='reconnected' and match_action[0]!='Chat':
                            match_player = pattern.search(lines[n]) # Search the pattern
                            playerName = lines[n][0:match_player.start()-1]
                            playerName = re.sub("'", "\\'", playerName)
                            if match_action[0]!='folds' and match_action[0]!='Folds' and match_action[0]!='checks':
                                match_amount = re.findall(r"(\d+(\.\d+)?)", lines[n]) # Search numbers
                                preflop_actions[playerName]={'action':match_action[0],'amount':match_amount[len(match_amount)-1][0]}
                            else:
                                preflop_actions[playerName]={'action':match_action[0],'amount':'0'}
                            logger.debug("preflop_actions[" + playerName + "]['action'] : " + preflop_actions[playerName]['action'])
                            logger.debug("preflop_actions[" + playerName + "]['amount'] : " + preflop_actions[playerName]['amount'])
                
                # Skip lines until ** Dealing Flop ** or #Game No
                while (n<nbLines):
                    n=inc_n(n, nbLines)
                    if n==nbLines : break

                    pattern = re.compile(r"^\*\* Dealing Flop \*\*|shows|show|^#Game No|wins") # Construct the pattern
                    match = pattern.search(lines[n]) # Search the pattern

                    if match:
                        if match[0]=="** Dealing Flop **":
                            flop=lines[n][21:-3]
                            flop=re.sub(" ","",flop)
                            logger.debug("flop : " + flop)

                            # Get flop actions
                            while (n<nbLines):
                                n=inc_n(n, nbLines)
                                if n==nbLines : break
                                #pattern = re.compile(r"all-In|raises|bets|calls|folds|Folds|checks|time|break|moved|disconnected|reconnected|Chat|^\*\* Dealing Turn \*\*|shows|show|^#Game No|wins|does") # Construit la pattern recherché
                                #pattern = re.compile(r"all-In|raises|bets|calls|folds|Folds|checks|^\*\* Dealing Turn \*\*|shows|show|^#Game No|wins|does") # Construit la pattern recherché
                                pattern = re.compile(r"^\*\* Dealing Turn \*\*|^#Game No|does|show|shows|wins") # Construit la pattern recherché
                                match_action = pattern.search(lines[n]) # Search the pattern
                                if match_action :
                                    n=n-1
                                    break
                                else:
                                    #pattern = re.compile("all-In|raises|bets|calls|folds|Folds|checks|time|break|moved|disconnected|reconnected|Chat") # Construct the pattern
                                    pattern = re.compile("all-In|raises|bets|calls|folds|Folds|checks") # Construct the pattern
                                    match_action = pattern.search(lines[n]) # Search the pattern
                                    if match_action : #!='time' and match_action[0]!='break' and match_action[0]!='moved' and match_action[0]!='disconnected' and match_action[0]!='reconnected' and match_action[0]!='Chat':
                                        match_player = pattern.search(lines[n]) # Search the pattern
                                        playerName = lines[n][0:match_player.start()-1]
                                        playerName = re.sub("'", "\\'", playerName)
                                        if match_action[0]!='folds' and match_action[0]!='Folds' and match_action[0]!='checks':
                                            match_amount = re.findall(r"(\d+(\.\d+)?)", lines[n]) # Search numbers
                                            flop_actions[playerName]={'action':match_action[0],'amount':match_amount[len(match_amount)-1][0]}
                                        else:
                                            flop_actions[playerName]={'action':match_action[0],'amount':'0'}
                                        logger.debug("flop_actions[" + playerName + "]['action'] : " + flop_actions[playerName]['action'])
                                        logger.debug("flop_actions[" + playerName + "]['amount'] : " + flop_actions[playerName]['amount'])
                            
                            # Skip lines until ** Dealing Turn ** or #Game No
                            while (n<nbLines):
                                n=inc_n(n, nbLines)
                                #if n==nbLines : break # Todo : Check why this line is commented
                                pattern = re.compile(r"^\*\* Dealing Turn \*\*|shows|show|^#Game No|wins")
                                match = pattern.search(lines[n]) # Search the pattern
                                if match:
                                    if match[0]=="** Dealing Turn **" :
                                        turn=lines[n][21:-3]
                                        logger.debug("turn : " + turn)

                                        # Get Turn actions
                                        while (n<nbLines):
                                            n=inc_n(n, nbLines)
                                            if n==nbLines : break
                                            #pattern = re.compile(r"all-In|raises|bets|calls|folds|Folds|checks|time|break|moved|disconnected|reconnected|Chat|^\*\* Dealing River \*\*|^#Game No|does") # Construit la pattern recherché
                                            #pattern = re.compile(r"all-In|raises|bets|calls|folds|Folds|checks|^\*\* Dealing River \*\*|^#Game No|does") # Construit la pattern recherché
                                            pattern = re.compile(r"^\*\* Dealing River \*\*|^#Game No|does") # Construit la pattern recherché
                                            match_action = pattern.search(lines[n]) # Recherche la pattern
                                            if match_action :
                                                n=n-1
                                                break
                                            else:
                                                #pattern = re.compile("all-In|raises|bets|calls|folds|Folds|checks|time|break|moved|disconnected|reconnected|Chat") # Construct the pattern
                                                pattern = re.compile("all-In|raises|bets|calls|folds|Folds|checks") # Construct the pattern
                                                match_action = pattern.search(lines[n]) # Search the pattern
                                                if match_action : #!='time' and match_action[0]!='break' and match_action[0]!='moved' and match_action[0]!='disconnected' and match_action[0]!='reconnected' and match_action[0]!='Chat':
                                                    match_player = pattern.search(lines[n]) # Construct the pattern
                                                    playerName = lines[n][0:match_player.start()-1]
                                                    playerName = re.sub("'", "\\'", playerName)
                                                    if match_action[0]!='folds' and match_action[0]!='Folds' and match_action[0]!='checks':
                                                        match_amount = re.findall(r"(\d+(\.\d+)?)", lines[n]) # Construct the pattern
                                                        turn_actions[playerName]={'action':match_action[0],'amount':match_amount[len(match_amount)-1][0]}
                                                    else:
                                                        turn_actions[playerName]={'action':match_action[0],'amount':'0'}
                                                    logger.debug("turn_actions[" + playerName + "]['action'] : " + turn_actions[playerName]['action'])
                                                    logger.debug("turn_actions[" + playerName + "]['amount'] : " + turn_actions[playerName]['amount'])
                                        
                                        
                                        # skip lines until ** Dealing River ** or #Game No
                                        while (n<nbLines):
                                            n=inc_n(n, nbLines)
                                            if n==nbLines : break
                                            pattern = re.compile(r"^\*\* Dealing River \*\*|shows|show|^#Game No|wins")
                                            match = pattern.search(lines[n]) # Search the pattern
                                            if match:
                                                if match[0]=="** Dealing River **":
                                                    river=lines[n][22:-3]
                                                    logger.debug("river : " + river)

                                                    # Get River actions
                                                    while (n<nbLines):
                                                        n=inc_n(n, nbLines)
                                                        if n==nbLines : break
                                                        #pattern = re.compile(r"all-In|raises|bets|calls|folds|Folds|checks|time|break|moved|disconnected|reconnected|Chat|shows|does|^#Game No") # Construct the pattern
                                                        #pattern = re.compile(r"all-In|raises|bets|calls|folds|Folds|checks|shows|does|^#Game No") # Construct the pattern
                                                        pattern = re.compile(r"shows|does|^#Game No") # Construct the pattern
                                                        match_action = pattern.search(lines[n]) # Search the pattern
                                                        if match_action :
                                                            n=n-1
                                                            break
                                                        else:
                                                            #pattern = re.compile("all-In|raises|bets|calls|folds|Folds|checks|time|break|moved|disconnected|reconnected|Chat") # Construct the pattern
                                                            pattern = re.compile("all-In|raises|bets|calls|folds|Folds|checks") # Construct the pattern
                                                            match_action = pattern.search(lines[n]) # Search the pattern
                                                            if match_action : #!='time' and match_action[0]!='break' and match_action[0]!='moved' and match_action[0]!='disconnected' and match_action[0]!='reconnected' and match_action[0]!='Chat':
                                                                match_player = pattern.search(lines[n]) # Search the pattern
                                                                playerName = lines[n][0:match_player.start()-1]
                                                                playerName = re.sub("'", "\\'", playerName)
                                                                if match_action[0]!='folds' and match_action[0]!='Folds' and match_action[0]!='checks':
                                                                    match_amount = re.findall(r"(\d+(\.\d+)?)", lines[n]) # Construct the pattern
                                                                    river_actions[playerName]={'action':match_action[0],'amount':match_amount[len(match_amount)-1][0]}
                                                                else:
                                                                    river_actions[playerName]={'action':match_action[0],'amount':'0'}
                                                                logger.debug("river_actions[" + playerName + "]['action'] : " + river_actions[playerName]['action'])
                                                                logger.debug("river_actions[" + playerName + "]['amount'] : " + river_actions[playerName]['amount'])
                                                    
                                                # match = #Game No or endfile
                                                else:
                                                    # n-1 to begin the next while loop on the good line
                                                    n=n-1
                                                    break
                                        # match = #Game No or endfile
                                    else: 
                                        # n-1 to begin the next while loop on the good line
                                        n=n-1
                                        break           
                                               
                        # match = #Game No or endfile
                        else:
                            # skip lines until shows or show or #Game No or wins
                            n=n-1
                            while (n<nbLines):
                                n=inc_n(n, nbLines)
                                match = re.search("does not|shows|show|^#Game No|wins", lines[n])
                                if match:
                                    if match[0]=="#Game No":
                                        n=n-1
                                        break
                                    
                                    if match[0]=="wins" :
                                        # Get Winners
                                        res=getWinners(winners, lines, n, nbLines)
                                        n=res["n"]
                                        winners=res["winners"]
                                    elif match[0]=="does not":
                                        continue
                                    elif match[0]=="shows" :
                                        shows_line=lines[n].split(" ")
                                        handPlayerName=shows_line[0]
                                        show_pos=1
                                        while shows_line[show_pos]!="shows" :
                                            handPlayerName=handPlayerName+" "+shows_line[show_pos]
                                            show_pos+=1
                                            
                                        handPlayerName=re.sub("'", "\\'", handPlayerName)
                                        handPlayer=shows_line[show_pos+2] + shows_line[show_pos+3]
                                        handPlayers[handPlayerName]=handPlayer
                                        logger.debug("handPlayers[" + handPlayerName + "] : " + handPlayers[handPlayerName])
                                    elif match[0]=="show" :
                                        shows_line=lines[n].split(" ")
                                        handPlayerName=shows_line[0]
                                        show_pos=1
                                        while shows_line[show_pos]!="doesn't":
                                            handPlayerName=handPlayerName+" "+shows_line[show_pos]
                                            show_pos+=1
                                        
                                        handPlayerName=re.sub("'", "\\'", handPlayerName)
                                        handPlayer=shows_line[show_pos+3] + shows_line[show_pos+4]
                                        handPlayers[handPlayerName]=handPlayer
                                        logger.debug("handPlayers[" + handPlayerName + "] : " + handPlayers[handPlayerName])                                                     
                            
                            # Break the main loop after got hands and winners
                            break       

                # Call API to record the hand
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
                    'players': json.dumps(players,ensure_ascii=False),
                    'handPlayers':json.dumps(handPlayers,ensure_ascii=False),
                    'smallBlindPlayer':smallBlindPlayer,
                    'smallBlind':smallBlind,
                    'bigBlindPlayer':bigBlindPlayer,
                    'bigBlind':bigBlind,
                    'preflop_actions':json.dumps(preflop_actions,ensure_ascii=False),
                    'flop_actions':json.dumps(flop_actions,ensure_ascii=False),
                    'turn_actions':json.dumps(turn_actions,ensure_ascii=False),
                    'river_actions':json.dumps(river_actions,ensure_ascii=False),
                    'winners':json.dumps(winners,ensure_ascii=False)}
                logger.debug("data : " + str(data))
            
                result=requests.post(api_url, data)
                obj=json.loads(result.content)
                logger.debug("API hand record result : " + str(obj))

                if n==nbLines :
                    logger.debug("End of file")
                    break