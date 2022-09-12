from urllib import response
import slack
import slack_logger
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import time
import pandas as pd

#indiquer le chemin env
env_path = Path('.') / '.env'
#charger variable d'environnement
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
#gerer evenements
slack_event_adapter = SlackEventAdapter(
    #evenements stockés dans slack/events
    os.environ['SIGNING_SECRET'],'/slack/events',app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']
#Ajout dans ce disctionnaire si nv message
message_count = {}
welcome_messages = {}
prise_meeting_id = {}


# Store conversation history
conversation_historys = []
nb_rdv=[]
nb_reaction=[]
reaction_off=[]
nb_msg=[]
# ID of the channel you want to send the message to
channel_id = "C04108VK9U5"
channel_id2 = "C02070ZMC7N"
# ID of user you watch to fetch information for




try:
    
   
    result = client.conversations_history(channel=channel_id, limit=50)
    # print(client.users_info(user=user_id)['user']['name'])
    # print(result2)
    # result2 = client.users_conversations(channel=channel_id, limit=2)
    # result2= client.conversations_info(channel=channel_id, limit=50)
    
    # listUser = client.users_list()
    # users = listUser["members"]
    #user_ids = list(map(lambda u: u["id"], users))
    
    #latest="",oldest=
    
    #conversations.repliespour chaque thread pour lequel vous souhaitez récupérer des messages.
    #users_list, conversations_listet usergroups_list pour recuperer nom des users
    # print(result2)
    conversation_historys = result['messages']
    # print(conversation_historys)
    # print(result.usersIdentity)
    # print(result)
    
    for conversation_history in conversation_historys:
        
        if conversation_history['text'] == "meeting":
            if conversation_history['reactions'][0]['name']== 'white_check_mark':
                # name_user=client.users_info(user=conversation_history['reactions'][0]['users'])['user']['name']
                # print(name_user)
                nb_rdv.append(client.users_info(user=conversation_history['reactions'][0]['users'][0])['user']['name'])
                count_meeting = pd.Series(nb_rdv).value_counts()
                
                # print(count_meeting)
            else:
                print('no')
        nb_msg.append(conversation_history['text'])
        # print(len(nb_msg))
        try:
            nb_reaction.append(conversation_history['reactions'][0]['name'])
            # print(nb_reaction)
        except:
            reaction_off.append("no")
    
       




    #conversation_user = result2
    
    
    #print(conversation_user)
    # Print results
    logging.info("{} messages found in {}".format(len(conversation_history), id))

except :
    logging.error("Error creating conversation: {}")


@ slack_event_adapter.on('message')
def message(payload):
    #print(payload)
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    #test=client.api_call('users.info')
    #print(test)
    print(channel_id)
    if BOT_ID != user_id and text=="meeting":
        client.chat_postMessage(channel=channel_id,text="Meeting réservé")
    # if text == "hey":
    #     client.chat_postMessage(channel=channel_id,text="Hello")
    
    #     count=count+1
    #     prise_meeting_id["id"] = user_id
    #     prise_meeting_id["nbMeeting"] = count
    #     client.chat_postMessage(channel=channel_id,text="l'user : "+prise_meeting_id["id"]+" à eu : "+str(prise_meeting_id["nbMeeting"])+" meeting")
    # # print(prise_meeting_id)
    # print(event)


    @ slack_event_adapter.on("reaction_added")
    def reaction_added(event_data):
        count=0
        emoji = event_data["event"]["reaction"]
        print(event_data["event"])
        
        
        
        if emoji=='white_check_mark' and text == "meeting":
            count=count+1
            client.chat_postMessage(channel=channel_id,text="l'user : "+event_data["event"]["user"]+" a réalisé un meeting")
            print(event_data["event"]["user"])
            print(count)
        if text != "meeting": 
            print("pas egal à meeting")
@app.route('/message-count', methods=['POST'])
def message_count():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    client.chat_postMessage(channel=channel_id,text="nombre de meeting pour chaque users : "+str(count_meeting))
    client.chat_postMessage(channel=channel_id,text="nombre de message aujourd'hui  : "+str(len(nb_msg)))
    client.chat_postMessage(channel=channel_id,text="nombre de message avec réaction : "+str(len(nb_reaction)))
    client.chat_postMessage(channel=channel_id,text="nombre de message sans réponse : "+str(len(reaction_off)))
    
    # print("nombre de meeting pour chaque users : "+str(count_meeting))
    return Response(), 200
    



    

if __name__=="__main__":
    #executer sur le port 5000
    app.run(debug=True)