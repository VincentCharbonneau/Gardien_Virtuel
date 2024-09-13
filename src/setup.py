from configparser import ConfigParser


#This code is not all mine, but I dont remember where I got it from. I will update this as soon as I find the source.

def runSetup():
    config_object = ConfigParser()
    accessToken = input("Enter your access token: ")
    clientId = input("Enter your client id: ")
    userId = input("Enter your user id: ")
    refresh = input("Enter your refresh freqieuncy (in seconds): ")

    config_object["config"] = {
        "accessToken": accessToken,
        "clientId": clientId,
        "userId": userId,
        "refreshfrequency": refresh
    }

    with open('config.ini', 'w') as conf:
        config_object.write(conf)
