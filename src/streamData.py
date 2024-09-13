#This code is not all mine, but I dont remember where I got it from. I will update this as soon as I find the source.

import sys, json, requests;
from os.path import exists;
import os;
from configparser import ConfigParser;
from setup import *;
from Beep import *;
import time





config_object = ConfigParser()
# Run setup from setup.py if config hasn't been created
if not exists('config.ini'):
    runSetup()

config_object.read("config.ini")
config = config_object["config"]
accessToken = config["accessToken"]
clientId = config["clientId"]
userId = config["userId"]



try:
    refreshFrequency = config["refreshFrequency"]
except KeyError:
    print("Error - make sure the theres a refreshFrequency in the config.ini file.")
    sys.exit(1)
except ValueError:
    print("Error - make sure the refreshFrequency is a number.")
    sys.exit(1)




listOfStreamer = []


def gatherData():
    # Define headers
    headers = {
        'Accept': 'application/vnd.twitchtv.v5+json',
        'Client-ID': clientId,
        'Authorization': 'Bearer ' + accessToken,
    }
    try:
        response = requests.get('https://api.twitch.tv/helix/streams/followed?user_id=' + userId, headers=headers)

        data = response.json()
        numStreams = len(data["data"])
        return (data, numStreams)

    except (KeyError, ValueError):
        print("Error - make sure the config is configured correctly.")
        sys.exit(1)

def printHeader():
    print ("\nCHANNEL " + ' '*13 + "GAME" + ' '*37 + "VIEWERS" + ' '*8 + "\n" + '-'*80)


def printStreamer(data, numStreams):
    printHeader()
    counter = 0
    listOfStreamer = []
    for i in range (0, numStreams):
        channelName = data["data"][i]["user_name"];
        channelGame = data["data"][i]["game_name"];
        channelViewers = str(data["data"][i]["viewer_count"]);
        streamType = data["data"][i]["type"];

        listOfStreamer.append(channelName)

        # Check if stream is actually live or VodCast
        if(streamType == "live"):
            streamType = "";
        else:
            streamType = "(vodcast)";

        #Truncate long channel names/games
        if(len(channelName) > 18):
            channelName = channelName[:18] + ".."
        if(len(channelGame) > 38):
            channelGame = channelGame[:38] + ".."

        #Formatting
        print ("{} {} {} {}".format(
        channelName.ljust(20),
        channelGame.ljust(40),
        channelViewers.ljust(8),
        streamType
        ))

        if (i == numStreams-1):
            print ('-'*80)

        counter += 1
    print("Nombre de chaines en ligne: ", counter)
    return listOfStreamer


def main():
    initialStreamer = printStreamer(*(gatherData()))
    while True:
        currentStreamer = printStreamer(*(gatherData()))
        if set(currentStreamer) == set(initialStreamer):
            pass
        else:
            makeBeep()
            initialStreamer = currentStreamer
        time.sleep(float(refreshFrequency))
        
        
        


if __name__ == "__main__":
    main()