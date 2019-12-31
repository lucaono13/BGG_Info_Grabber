import requests
import json
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from time import sleep
import csv

#Empty list for input
game_ids = []

# Input number of board games that you are adding
n = int(input("Enter number of board games: "))

# Input each BGG ID
for i in range(0,n):
    ele = int(input("BGG ID: "))
    game_ids.append(ele)

# Creates board games DF
boardgames = pd.DataFrame(columns =['Name','Categories','Mechanics','Min. Players','Max Players','BGG Rank','BGG Score','Complexity','Playtime','Owner','Year','Expansions Avail.','Expansion Names','Image','Link'])
print("\nEmpty DF Created!\n")

print("Starting board game entry...\n")

# for loop that goes through entire game_ids list in order to create a DF with
for id in range(len(game_ids)):
    # creates the API link for the board game. Uses the XML API 2 created by BGG
    link = "https://api.geekdo.com/xmlapi2/thing?id={}&stats=1".format(game_ids[id])

    # GET request for the API
    r = requests.get(link)

    # formats XML
    root = ET.fromstring(r.content)

    # Variables to be used in the DF
    url ="https://boardgamegeek.com/boardgame/{}".format(game_ids[id])
    designers = []
    categories = []
    mechanisms = []
    year = 0
    name = ""
    min_play = 0
    max_play = 0
    rank = 0
    score = 0.0
    weight = 0.0
    mintime = ''
    maxtime = ''
    expan = []
    expan_c = 0
    img = ""
    thb = ""

    # for loop that goes through each line in the XML
    for child in root.iter('*'):

        # To get the board game designer(s), categories and mechanisms
        for link in child.findall('link'):
            if(link.get('type') == 'boardgamedesigner'):
                des = link.get('value')
                designers.append(des)
            elif(link.get('type') == 'boardgamecategory'):
                cat = link.get('value')
                categories.append(cat)
            elif(link.get('type') == 'boardgamemechanic'):
                mec = link.get('value')
                mechanisms.append(mec)
            elif(link.get('type') == 'boardgameexpansion'):
                expan_c += 1
                exp = link.get('value')
                expan.append(exp)

        # year published
        if(child.tag == 'yearpublished'):
            year = child.get('value')
        # minimum players
        elif(child.tag == 'minplayers'):
            min_play = child.get('value')
        # maximum players
        elif(child.tag == 'maxplayers'):
            max_play = child.get('value')
        # game name
        elif(child.tag == 'name'):
            if(child.get('type') == 'primary'):
                name = child.get('value')
        # BGG rank
        elif(child.tag == 'rank'):
            if(child.get('friendlyname') == 'Board Game Rank'):
                rank = child.get('value')
        # BGG score
        elif(child.tag == 'average'):
            score = child.get('value')
        # BGG Complexity Rating
        elif(child.tag == 'averageweight'):
            weight = child.get('value')
        # Game thumbnail
        elif(child.tag == 'thumbnail'):
            thb = child.text
        # Game image
        elif(child.tag == 'image'):
            img = child.text
        # minimum playtime in minutes
        elif(child.tag == 'minplaytime'):
            mintime = child.get('value')
        # maximum playtime in minutes
        elif(child.tag == 'maxplaytime'):
            maxtime = child.get('value')

    # creates a time range with mintime and maxtime
    time = mintime + "-" + maxtime + " min"

    owners = input("Who owns " + name + "?: ")


    # appends data to the created DF
    boardgames = boardgames.append({'Name':name,'Year':year,'Categories':categories,'Mechanics':mechanisms,'Min. Players':min_play,'Max Players':max_play,'BGG Rank':rank,'BGG Score':score,'Complexity':weight,'Playtime':time,'Owner':owners,'Expansions Avail.':expan_c,'Expansion Names':expan,'Link':url,'Image':img},ignore_index=True)
    # get current time
    time = datetime.now()
    ct = time.strftime("%H:%M:%S")
    # prints out the time the game was added to DF
    print(name + " ("+ rank + ") added to DF at " + ct)
    # waits 7 seconds before continuing as to not overload server
    sleep(2)

    #Downloads box art
    name2 = name.replace(":"," -")
    print("     Downloading image of " + name + " box art.\n")
    pic = requests.get(img, stream = True)
    imgname = "Box Art\\" + name2 + "_art.jpg"
    with open(imgname, 'wb') as f:
        for chunk in pic:
            f.write(chunk)
    sleep(5)


print("\nAll board games added.\nAll images downloaded to 'Box Art' Folder.")

# Gets current time in order to make make .csv file
now = datetime.now()
dt_string = now.strftime("%m-%d-%Y_%H-%M")

# creates filename that has date and time created in the name
filename = "Exported_DF\\boardgames_" + dt_string +".csv"

# Creating string list from certain columns
boardgames['Categories'] = [', '.join(map(str,l)) for l in boardgames['Categories']]
boardgames['Mechanics'] = [', '.join(map(str,l)) for l in boardgames['Mechanics']]
boardgames['Expansion Names'] = [', '.join(map(str,l)) for l in boardgames['Expansion Names']]

boardgames.to_csv(filename, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
print("New .csv file created!")

print(".csv file name: " + filename + "\n")

print("Done!")

sleep(20)
#exit()
