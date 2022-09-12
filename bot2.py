import logging
import json
import os
import time
import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter

from slack_manager import SlackManager


#indiquer le chemin env
env_path = Path('.') / '.env'
#charger variable d'environnement
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
#gerer evenements
slack_event_adapter = SlackEventAdapter(
    #evenements stockés dans slack/events
    os.environ['SIGNING_SECRET'],'/slack/events',app)

client = SlackManager()
TOKEN = os.environ['SLACK_TOKEN']
# BOT_ID = client.api_call("auth.test")['user_id']
#Ajout dans ce disctionnaire si nv message
message_count = {}
message_count_week = {}
message_count_month = {}
welcome_messages = {}
prise_meeting_id = {}


# Store conversation history
conversation_historys = []
conversation_history_weeks = []
nb_rdv=[]
nb_rdv_week=[]
nb_reaction=[]
reaction_off=[]
nb_msg=[]

channel_id = "C04108VK9U5"
channel_id2 = "C02070ZMC7N"
user_id="U039UV80U85"

channel_hunters = "C02070ZMC7N"



# try : 
#     oldest2 = time.time()-7*86400
#     result2 = client.conversations_history(channel=channel_id2, oldest=oldest2)

#     conversation_history_weeks = result2['messages']
#     for conversation_history_week in conversation_history_weeks:
#         # print(client.users_info(user=conversation_history['user'])['user']['name'])
#         texte=conversation_history_week['text'].lower()
#         if "meeting" in texte:
#             print("week")
#             # name_user=client.users_info(user=conversation_history['reactions'][0]['users'])['user']['name']
#             # print(name_user)
#             nb_rdv_week.append(client.users_info(user=conversation_history_week['user'])['user']['name'])
#             # print(count_meeting_week)
#             logging.info("{} messages found in {}".format(len(conversation_history_week), id))
#     count_meeting_week = pd.Series(nb_rdv_week).value_counts()
# except :
#     logging.error("Error creating conversation: {}")   


# try:
    
#     oldest = time.time()-1*86400
#     result = client.conversations_history(channel=channel_id2, oldest=oldest)
    
#     # listUser = client.users_list()
#     # users = listUser["members"]
#     #user_ids = list(map(lambda u: u["id"], users))

#     conversation_historys = result['messages']
    
#     for conversation_history in conversation_historys:
#         # print(client.users_info(user=conversation_history['user'])['user']['name'])
#         texte=conversation_history['text'].lower()
#         if "meeting" in texte:
#             print("days")    
#                 # name_user=client.users_info(user=conversation_history['reactions'][0]['users'])['user']['name']
#                 # print(name_user)
#             nb_rdv.append(client.users_info(user=conversation_history['user'])['user']['name'])
#             logging.info("{} messages found in {}".format(len(conversation_history), id))
#     count_meeting = pd.Series(nb_rdv).value_counts()
# except :
#     logging.error("Error creating conversation: {}")

def count_messages(seconds=24*60*60):
    meetings = {}
    id_to_user = {}
    try : 
        oldest = time.time() - seconds
        results = client.channel_history_iter(
            token=TOKEN,
            channel=channel_hunters, 
            oldest=oldest
            )
        logging.error("HEERE")
        # logging.error(f"history length: {len(result['messages'])}")
        # conversation_history_weeks = result['messages']
        for message in results:
            logging.error(f"message content : {message}")
            text = message['text'].lower()
            if "meeting" not in text:
                continue

            user_id = message['user']
            if user_id not in id_to_user:
                user_name = client._client.users_info(user=user_id)['user']['name']
                id_to_user[user_id] = user_name

            user_name = id_to_user[user_id]
            if user_name not in meetings:
                meetings[user_name] = 0
            meetings[user_name] +=1
    except Exception as e:
        logging.error(f"Error creating conversation: {e}")   
    finally:
        return meetings
@app.route('/message-count', methods=['POST'])
def message_count():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    count_meeting = count_messages(seconds=1*24*3600)
    # client.post_file(
    #     token=TOKEN,
    #     channel=channel_id,
    #     content=str(count_meeting),
    #     filename="nombre de meeting pour chaque users ce jour",
    # )    
    # client.chat_postMessage(channel=channel_id,text="nombre de message aujourd'hui  : "+str(len(nb_msg)))
    # client.chat_postMessage(channel=channel_id,text="nombre de message avec réaction : "+str(len(nb_reaction)))
    # client.chat_postMessage(channel=channel_id,text="nombre de message sans réponse : "+str(len(reaction_off)))
    
    # print("nombre de meeting pour chaque users : "+str(count_meeting))
    response = app.response_class(
        response=json.dumps(count_meeting),
        mimetype='application/json'
    )
    return response
    # return Response(count_meeting), 200
@app.route('/message-count-week', methods=['POST'])
def message_count_week():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    count_meeting_week = count_messages(seconds=7*24*3600)
    # client.post_file(
    #     token=TOKEN,
    #     channel=channel_id,
    #     content=str(count_meeting_week),
    #     filename="nombre de meeting pour chaque users cette semaine",
    # )
    # client.chat_postMessage(channel=channel_id,text="nombre de message aujourd'hui  : "+str(len(nb_msg)))
    # client.chat_postMessage(channel=channel_id,text="nombre de message avec réaction : "+str(len(nb_reaction)))
    # client.chat_postMessage(channel=channel_id,text="nombre de message sans réponse : "+str(len(reaction_off)))
    
    # print("nombre de meeting pour chaque users : "+str(count_meeting))

    response = app.response_class(
        response=json.dumps(count_meeting_week),
        mimetype='application/json'
    )
    return response

    # return Response(count_meeting_week), 200

@app.route('/message-count-month', methods=['POST'])
def message_count_month():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    count_meeting_month = count_messages(seconds=29*24*3600)
    client.post_file(
        token=TOKEN,
        channel=channel_id,
        content=str(count_meeting_month),
        filename="nombre de meeting pour chaque users ce mois",
    )
    # client.chat_postMessage(channel=channel_id,text="nombre de message aujourd'hui  : "+str(len(nb_msg)))
    # client.chat_postMessage(channel=channel_id,text="nombre de message avec réaction : "+str(len(nb_reaction)))
    # client.chat_postMessage(channel=channel_id,text="nombre de message sans réponse : "+str(len(reaction_off)))
    
    # print("nombre de meeting pour chaque users : "+str(count_meeting))
    return Response(), 200

    
# /csv
# /month


    

if __name__=="__main__":
    #executer sur le port 5000
    app.run(debug=True)