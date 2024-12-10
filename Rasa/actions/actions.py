# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
import json
from pathlib import Path
from typing import Any, Text, Dict, List
import requests
from bs4 import BeautifulSoup
import re
import urllib.request
from PIL import Image
from rasa_sdk.events import SlotSet
import emoji
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase


class ActionFindInfo(Action):
    
    def name(self) -> Text:
        return "action_find_info"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = ""
        output=""
        name = str(tracker.get_slot('player_name'))
        name = name.replace(' ','+')    
        url = requests.get("https://www.transfermarkt.it/schnellsuche/ergebnis/schnellsuche?query="+name,headers={'User-Agent': 'Custom'})

        if url.status_code == 200:
            htmltext = url.text
            soup = BeautifulSoup(htmltext,features="lxml")
            playercode = soup.find("div", {"id" : "yw0"})
            playercode = playercode.find("tr", {"class" : "odd"})
            if playercode != None:
                playercode = playercode.find("td", {"class" : "hauptlink"})
                playercode = playercode.find("a")
                playercode = playercode.get('href')
                

                player = 'https://www.transfermarkt.it'+str(playercode)
                urlPlayer = requests.get(player,headers={'User-Agent': 'Custom'})

                if urlPlayer.status_code == 200:
                    
                    htmlplayer = urlPlayer.text
                    soup = BeautifulSoup(htmlplayer,features="lxml")
                    marketValue = soup.find("a", {"class" : "data-header__market-value-wrapper"})

                    playername = soup.find("h1", {"class" : "data-header__headline-wrapper"})
                    playername = playername.text
                    playername = " ".join(playername.split())

                    num = playername.split(' ')[0]
                    match = re.search(' ', playername)
                    if match:
                        nome = playername[match.end():]
                    else:
                        nome = ''
                    team = soup.findAll("span", {"class" : "info-table__content info-table__content--bold info-table__content--flex"})
                    team = team[1]
                    team = team.findAll("a")
                    team = team[1]
                    team = team.text
                        
                    #output = "Il giocatore cercato è "+ str(nome) + ", il suo numero è "+ str(num)
                    output = "Ho trovato questo calciatore:\n"+ str(nome) +" della squadra "+ str(team)
                    #Photo
                    photo = soup.find("div",{"class":"data-header__profile-container"})
                    photo = photo.find("img", {"class" : "data-header__profile-image"})
                    photo = photo.get('src')
                    # print(num)
                    # print(nome)
                else:
                    output = "C'è stato un errore nella richiesta"    
            else: 
                output = 'Non ho trovato nessun giocatore. Si prega di riprovare' 
        else:
            output = "C'è stato un errore nella richiesta"
        dispatcher.utter_message(text = output)
        if photo != None:
            dispatcher.utter_message(image = photo)
        return []

class ActionInfoPlayer(Action):
    
    def name(self) -> Text:
        return "action_info_player"
    
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name = ""
        output=""
        name = str(tracker.get_slot('player_name'))
        info = str(tracker.get_slot('info'))
        name = name.replace(' ','+')    
        url = requests.get("https://www.transfermarkt.it/schnellsuche/ergebnis/schnellsuche?query="+name,headers={'User-Agent': 'Custom'})

        if url.status_code == 200:
            htmltext = url.text
            soup = BeautifulSoup(htmltext,features="lxml")
            playercode = soup.find("div", {"id" : "yw0"})
            playercode = playercode.find("tr", {"class" : "odd"})
            if playercode != None:
                playercode = playercode.find("td", {"class" : "hauptlink"})
                playercode = playercode.find("a")
                playercode = playercode.get('href')
                

                player = 'https://www.transfermarkt.it'+str(playercode)
                urlPlayer = requests.get(player,headers={'User-Agent': 'Custom'})

                if urlPlayer.status_code == 200:
                    urlPlayer = requests.get(player,headers={'User-Agent': 'Custom'})
                    if urlPlayer.status_code == 200:
                        if info == "info":
                                htmlplayer = urlPlayer.text
                                soup = BeautifulSoup(htmlplayer,features="lxml")
                                #MarketValue
                                marketValue = soup.find("a", {"class" : "data-header__market-value-wrapper"})
                                marketValue = marketValue.text
                                marketValue = marketValue.split('€')
                                value = marketValue[0]
                                marketValue[1] = marketValue[1].split(':')
                                update = marketValue[1][1]
                                maxValue = soup.find("div", {"class" : "tm-player-market-value-development__max-value"})
                                maxValue = maxValue.text
                                
                                extraction = soup.find("h1", {"class" : "data-header__headline-wrapper"})
                                extraction = extraction.text
                                playername = " ".join(extraction.split())

                                num = playername.split(' ')[0]
                                match = re.search(' ', playername)
                                if match:
                                    nome = playername[match.end():]
                                else:
                                    nome = ''
                                    
                                
                                #Team
                                team = ""
                                team = soup.findAll("span", {"class" : "info-table__content info-table__content--bold info-table__content--flex"})
                                team = team[1]
                                team = team.findAll("a")
                                team = team[1]
                                team = team.text
                                #BirthDate
                            
                                extraction = soup.find("span", {"itemprop" : "birthDate"})
                                extraction = extraction.text
                                birthDate = " ".join(extraction.split())
                               
                                #Flag
                                flag = soup.find("div", {"class" : "data-header__info-box"})
                                flag = flag.find("img", {"class" : "flaggenrahmen"})
                                flag = flag.get('title')
                                #BirthPlace
                                birthPlace = soup.find("span", {"itemprop" : "birthPlace"})
                                if birthPlace.find("span") != None: 
                                    birthPlace = birthPlace.find("span")   
                                    birthPlace = birthPlace.get('title')
                                else:      
                                    birthPlace = birthPlace.text
                                    birthPlace = " ".join(birthPlace.split())
                                #Height
                                extraction = soup.find("span", {"itemprop" : "height"})
                                extraction = extraction.text
                                height = " ".join(extraction.split())
                                
                                #Position
                                information = soup.find("div", {"class" : "data-header__details"})
                                position = information.findAll("ul", {"class" : "data-header__items"})
                                position = position[1].findAll("li")
                                extraction = position[1].find("span", {"class":"data-header__content"})
                                extraction = extraction.text
                                position = " ".join(extraction.split())
                                
                                #Photo
                                photo = soup.find("div",{"class":"data-header__profile-container"})
                                photo = photo.find("img", {"class" : "data-header__profile-image"})
                                photo = photo.get('src')
                              
                                output = "Il giocatore {}, appartenente alla squadra {}, è nato il {} a {} ({}), è alto {} e gioca nel ruolo di {} ".format(nome,team,birthDate,birthPlace,flag,height,position)
                                label = emoji.emojize("Ecco le informazioni personali del calciatore " 
                                                   + nome + '\n'+':backhand_index_pointing_down_light_skin_tone: ')
                                market = emoji.emojize(':euro_banknote: Valore di mercato attuale: '+ value + '€\n'+
                                                       ':spiral_calendar: Ultimo aggiornamento:'+ update +'\n'+
                                                       ':bar_chart: Valore più alto raggiunto: '+ maxValue)
                                dispatcher.utter_message(text = label)
                                dispatcher.utter_message(image = photo)
                                dispatcher.utter_message(text = output)
                                dispatcher.utter_message(text = market)
                        elif info == "stats":
                            idPlayer = playercode.rsplit('/', 1)[1]
                            urlPerformance = requests.get("https://www.transfermarkt.it/ceapi/player/"+str(idPlayer)+"/performance",headers={'User-Agent': 'Custom'})

                            statsplayer = urlPerformance.text
                            if statsplayer == '[]':
                                output = 'Nessuna statistica'
                            else:
                                htmlplayer = urlPlayer.text
                                soupPlayer = BeautifulSoup(htmlplayer,features="lxml")
                                extraction = soupPlayer.find("h1", {"class" : "data-header__headline-wrapper"})
                                extraction = extraction.text
                                playername = " ".join(extraction.split())
                                match = re.search(' ', playername)
                                if match:
                                    nome = playername[match.end():]
                                else:
                                    nome = ''
                                label = emoji.emojize("Ecco le statistiche della stagione corrente del calciatore " 
                                                   + nome +':backhand_index_pointing_down_light_skin_tone:')
                                dispatcher.utter_message(text = label)    
                                stats = statsplayer.split('}')
                                #stats = stats.split('')
                                res = {}
                                count = 0
                                for i in stats:
                                    i = i + '}'
                                    i = re.sub(r'^.*?{', '{', i)
                                    res[count] = i
                                    count = count + 1
                                res.pop(count-1)
                               
                                for i in res:
                                    res[i] = json.loads(res[i])
                                    if(res[i]['goalkeeper'] == False):   
                                        output = emoji.emojize(':trophy: Competizione: '+ res[i]['competitionDescription']+'\n'+
                                            ':input_numbers: Partite giocate: '+ str(res[i]['gamesPlayed'])+'\n'+
                                            ':soccer_ball: Goal fatti: '+ str(res[i]['goalsScored'])+'\n'+
                                            ':running_shoe: Assist: '+ str(res[i]['assists'])+'\n'+
                                            ':yellow_square: Cartellini gialli: '+ str(res[i]['yellowCards'])+'\n'+
                                            ':red_square: Cartellini rossi: '+ str(res[i]['redCards'])+'\n'+
                                            ':t-shirt: Percentuale di partite da titolare: '+ str(round(res[i]['startElevenPercent'],2))+"%"+'\n'+  
                                            ':nine_o’clock: Percentuale di minuti in campo: '+ str(round(res[i]['minutesPlayedPercent'],2))+"%")
                                    else:
                                        output = emoji.emojize(':trophy: Competizione: '+ res[i]['competitionDescription']+'\n'+
                                            ':soccer_ball: Goal subiti: '+ str(res[i]['concededGoals'])+'\n'+
                                            ':goal_net: Clean sheets: '+ str(res[i]['cleanSheets'])+'\n'+
                                            ':gloves: Rigori parati: '+ str(res[i]['blockedPenaltyPercent'])+"%"+'\n'+
                                            ':mantelpiece_clock: Minuti giocati: '+ str(res[i]['minutesPlayed'])+'\n'+
                                            ':nine_o’clock: Percentuale di minuti in campo: '+ str(round(res[i]['minutesPlayedPercent'],2))+"%")
                                    dispatcher.utter_message(text = output)    
                        elif info == "transfer":
                            htmlplayer = urlPlayer.text
                            soup = BeautifulSoup(htmlplayer,features="lxml")
                            transfer= soup.find("div",{"data-viewport": "Transferhistorie"})
                            transfer = transfer.findAll("div",{"class": "grid tm-player-transfer-history-grid"})
                            table = ""
                            extraction = soup.find("h1", {"class" : "data-header__headline-wrapper"})
                            extraction = extraction.text
                            playername = " ".join(extraction.split())
                            match = re.search(' ', playername)
                            if match:
                                nome = playername[match.end():]
                            else:
                                nome = ''
                                
                            output = emoji.emojize("Ecco la cronologia trasferimenti del calciatore " 
                                                   + nome + '\n'+':backhand_index_pointing_down_light_skin_tone:')
                            
                            dispatcher.utter_message(text = output)    
                            output = "Stagione" + '                    '+ "Trasferimento" + '                     ' + "Costo"
                            dispatcher.utter_message(text = output)
                            for item in transfer:
                                season = item.find("div",{"class": "grid__cell grid__cell--center tm-player-transfer-history-grid__season"})
                                season = season.text
                                season = " ".join(season.split())
                                date = item.find("div",{"class": "grid__cell grid__cell--center tm-player-transfer-history-grid__date"})
                                date = date.text
                                date = " ".join(date.split())
                                oldclub = item.find("div",{"class": "grid__cell grid__cell--center tm-player-transfer-history-grid__old-club"})
                                oldclub = oldclub.text
                                oldclub = " ".join(oldclub.split())
                                newclub = item.find("div",{"class": "grid__cell grid__cell--center tm-player-transfer-history-grid__new-club"})
                                newclub = newclub.text
                                newclub = " ".join(newclub.split())
                                marketvalue = item.find("div",{"class": "grid__cell grid__cell--center tm-player-transfer-history-grid__market-value"})
                                marketvalue = marketvalue.text
                                marketvalue = " ".join(marketvalue.split())
                                if marketvalue == "-": marketvalue = "n.d."
                                cost = item.find("div",{"class": "grid__cell grid__cell--center tm-player-transfer-history-grid__fee"})
                                cost = cost.text
                                cost = " ".join(cost.split())
                                if cost == "-" or cost == "gratuito": cost = (emoji.emojize(':FREE_button: '  ))
                                elif cost == "Prestito" : cost = (emoji.emojize(':left-right_arrow: ' + cost  )) 
                                elif cost == "Fine prestito" : cost = (emoji.emojize(':BACK_arrow: ' + cost  ))
                                elif cost == "?" : cost = (emoji.emojize(':red_question_mark: n.d.'  ))    
                                else: cost = (emoji.emojize(':money_bag: ' + cost  ))   
                                movement = (emoji.emojize(oldclub + ' :airplane_departure: :right_arrow: :airplane_arrival: '+newclub ))
                                season = (emoji.emojize(':spiral_calendar: ' + season ))
                                
                                row = (season + '     '+ movement + '     ' + cost+'\n')
                                table = table + row
                            dispatcher.utter_message(text = table)
                else:
                    output = "C'è stato un errore nella richiesta"         
        else:
            output = "C'è stato un errore nella richiesta"    
            
        
        
        return []
    
class ActionFindTeam(Action):
    
    def name(self) -> Text:
        return "action_find_team"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = ""
        output=""
        name = str(tracker.get_slot('team_name'))
        name = name.replace(' ','+')    
        url = requests.get("https://www.transfermarkt.it/schnellsuche/ergebnis/schnellsuche?query="+name,headers={'User-Agent': 'Custom'})

        if url.status_code == 200:
            htmltext = url.text
            soup = BeautifulSoup(htmltext,features="lxml")
            soup = soup.find("main")
            tables = soup.findAll("div",{"class" : "row"})
            check = False
            for item in tables:
                result = item.find("h2",{"class" : "content-box-headline"}).text
                if "Risultati società" in result:
                    check = True
                    soup = item
                    break
            if check == False:
                output = 'Non ho trovato nessun risultato. Si prega di riprovare' 
            else:
                squadcode = soup.find("div", {"class" : "grid-view"})
                if squadcode != None:
                    squadcode = squadcode.find("td", {"class" : "hauptlink"})
                    squadcode = squadcode.find("a")
                    squadcode = squadcode.get('href')
                    

                    squad = 'https://www.transfermarkt.it'+str(squadcode)
                    urlSquad = requests.get(squad,headers={'User-Agent': 'Custom'})

                    if urlSquad.status_code == 200:
                        
                        htmlSquad = urlSquad.text
                        soup = BeautifulSoup(htmlSquad,features="lxml")
                        
                        # Team Market Value
                        teamMarketValue = soup.find("a", {"class" : "data-header__market-value-wrapper"}).text
                        teamMarketValue = teamMarketValue.split('€')
                        teamMarketValue = teamMarketValue[0]
                        
                        #Photo
                        photo = soup.find("div",{"class":"data-header__profile-container"})
                        photo = photo.find("img")
                        photo = photo.get('src')
                        
                        #Team Name
                        nomeTeam = soup.find("h1", {"class" : "data-header__headline-wrapper data-header__headline-wrapper--oswald"}).text
                        nomeTeam = " ".join(nomeTeam.split())

                        playername = soup.find("h1", {"class" : "data-header__headline-wrapper"})
                        playername = playername.text
                        playername = " ".join(playername.split())

                        roster = soup.find("div", {"id" : "yw1"})
                        roster = roster.find("tbody")
                        if roster == None:
                            output = "Non è stato trovato nessun risultato."
                        else:
                            players = roster.findAll("tr",{"class" : ['odd', 'even']})
                            goalkeepers = emoji.emojize(":gloves:                        PORTIERI\n")
                            defenders = emoji.emojize(":locked:                        DIFENSORI\n")
                            midfielders = emoji.emojize(":running_shoe:                        CENTROCAMPISTI\n")
                            forwards = emoji.emojize(":soccer_ball:                            ATTACCANTI\n")
                            for player in players:
                                role = player.find('td').get('title')
                                table = player.find("table",{"class":"inline-table"})
                                nome = table.find("td",{"class":"hauptlink"}).find("a")
                                nome = nome.text
                                # Ruolo
                                ruolo = table.findAll("tr")
                                ruolo = ruolo[1].text
                                words = ruolo.split()
                                letters = [word[0] for word in words]
                                ruolo = "".join(letters)
                                ruolo = ruolo.upper()
                                if ruolo == "CDD": ruolo = "ED"
                                elif ruolo == "CDS": ruolo = "ES"
                                elif ruolo == "P": ruolo = "Por"
                                elif ruolo == "M": ruolo = "Med"
                                elif ruolo == "C": ruolo = "CC"
                                elif ruolo == "T": ruolo = "Trq"
                                
                                # BirthDate
                                columns = player.findAll("td",{"class":"zentriert"})
                                birthDate = columns[1].text
                                birthDate = birthDate[birthDate.find('('):]
                                
                                # Flag
                                flag = columns[2].find("img", {"class" : "flaggenrahmen"}).get('title')
                                flag = flag.lower()
                                flag = flag.replace(' ','_')
                                flag = flag.replace("'",'’')
                                flag = flag.replace("olanda",'paesi_bassi')
                                flag = flag.replace("bosnia-erzegovina", 'bosnia_ed_erzegovina')
                                flag = flag.replace("congo", 'congo-brazzaville')
                                flag = flag.replace("irlanda_del_nord", 'regno_unito')                               	
                                flag = emoji.emojize(':bandiera_'+ flag + ':',language='it')
                                
                                # MarketValue
                                marketValue = player.find("td", {"class" : "rechts hauptlink"}).text
                                if not (marketValue and marketValue.strip()): marketValue = 'n.d.'
                                
                                # Message
                                if role == 'Porta':
                                    goalkeepers += (nome + '\t\t\t\t' + ruolo + '\t\t\t\t' + birthDate + '\t\t\t\t' + flag + '\t\t\t\t' + marketValue + '\n')
                                elif role == 'Difesa':
                                    defenders += (nome + '\t\t\t\t' + ruolo + '\t\t\t\t' + birthDate + '\t\t\t\t' + flag + '\t\t\t\t' + marketValue + '\n')
                                elif role == 'Centrocampo':
                                    midfielders += (nome + '\t\t\t\t' + ruolo + '\t\t\t\t' + birthDate + '\t\t\t\t' + flag + '\t\t\t\t' + marketValue + '\n')
                                elif role == 'Attaccante':
                                    forwards += (nome + '\t\t\t\t' + ruolo + '\t\t\t\t' + birthDate + '\t\t\t\t' + flag + '\t\t\t\t' + marketValue + '\n')   
                            # Utter Message
                            message = emoji.emojize("Ecco la rosa della squadra " + nomeTeam
                                                    + '\n'+':backhand_index_pointing_down_light_skin_tone:')
                            # Total Value
                            totalValue = emoji.emojize(":bank: Il valore totale della squadra " + nomeTeam + " è " + teamMarketValue + '€')
                            
                            dispatcher.utter_message(text = message)
                            dispatcher.utter_message(image = photo)
                            label = "Nome" + '              '+ "Ruolo" + '       ' + "Età"+ '     '+"Nazionale" + '     '+ "Valore"
                            dispatcher.utter_message(text = label)
                            dispatcher.utter_message(text = goalkeepers)
                            dispatcher.utter_message(text = defenders)
                            dispatcher.utter_message(text = midfielders)
                            dispatcher.utter_message(text = forwards)
                            dispatcher.utter_message(text = totalValue)
                    else:
                        output = "C'è stato un errore nella richiesta"    
                else: 
                    output = 'Non ho trovato nessun risultato. Si prega di riprovare' 
        else:
            output = "C'è stato un errore nella richiesta"
        dispatcher.utter_message(text = output)
        return []
    
class ActionChooseInfo(Action):
    
    def name(self) -> Text:
        return "action_choose_info"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(response = "utter_choose_info")
        return []
    

class MyFallback(Action):
    
    def name(self) -> Text:
        return "action_my_fallback"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(response = "utter_fallback")
        return []