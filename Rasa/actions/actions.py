# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
from bs4 import BeautifulSoup
import re
import json

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []

class ActionSearchPlayer(Action):

    def name(self) -> Text:
        return "action_search_player"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #name = str(tracker.get_slot('player_name'))
        #name = name.replace(' ','+')    
        url = requests.get("https://www.transfermarkt.it/schnellsuche/ergebnis/schnellsuche?query=Kessie",headers={'User-Agent': 'Custom'})

        if url.status_code == 200:
            htmltext = url.text
            soup = BeautifulSoup(htmltext)
            playercode = soup.find("tr", {"class" : "odd"})
            if playercode != None:
                playercode = playercode.find("td", {"class" : "hauptlink"})
                playercode = playercode.find("a")
                playercode = playercode.get('href')
                #print(playercode)

                player = 'https://www.transfermarkt.it'+str(playercode)
                urlPlayer = requests.get(player,headers={'User-Agent': 'Custom'})

                if url.status_code == 200:

                    htmlplayer = urlPlayer.text
                    soup = BeautifulSoup(htmlplayer)
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
                    output = "Il giocatore cercato è "+ str(nome) + ", il suo numero è "+ str(num) + "e il suo valore è " + str(marketValue) +" mln"
                    # print(num)
                    # print(nome)
                else:
                    output = "C'è stato un errore nella richiesta"    
            else: 
                output = 'Non ho trovato nessun giocatore. Si prega di riprovare' 
        else:
            output = "C'è stato un errore nella richiesta"
        dispatcher.utter_message(text = output)
        return []
