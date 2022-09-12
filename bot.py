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
import operator
import datetime

from IPython.display import display

                    


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
message_count_day = {}
message_count_week = {}
message_count_last_week = {}
message_count_last_month = {}
message_count_month = {}
welcome_messages = {}
prise_meeting_id = {}
reseller_month = {}
check_month = {}
dict_check={}


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
#numero jours du mois
mois=datetime.datetime.today().day
#numero jours de la semaine
semaine=datetime.datetime.today().isoweekday()



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

def count_messages(seconds=24*60*60, seconds2=0):
    meetings = {}
    id_to_user = {}
    try : 
        oldest = time.time() - seconds
        # latest = time.time() - seconds2
        results = client.channel_history_iter(
            token=TOKEN,
            channel=channel_hunters, 
            oldest=oldest,
            # latest=latest
            )
        # logging.error(results)   
        # logging.error("HEERE")
        # logging.error(f"history length: {len(result['messages'])}")
        # conversation_history_weeks = result['messages']
        for message in results:
            # logging.error(f"message content : {message}")
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

def count_check_month(seconds=24*60*60, seconds2=0):
    check_m = {}
    id_to_user = {}
    
    try : 
        oldest = time.time() - seconds
        # latest = time.time() - seconds2
        results = client.channel_history_iter(
            token=TOKEN,
            channel=channel_hunters, 
            oldest=oldest,
            # latest=latest
            )
        # logging.error(results)   
        # logging.error("HEERE")
        # logging.error(f"history length: {len(result['messages'])}")
        # conversation_history_weeks = result['messages']
        for message in results:
            
            
            if message['reactions'][0]['name']== 'white_check_mark':
                text = message['text'].lower()
                text_normal=text.split(";")
                if "meeting" not in text:
                    continue
                user_id = message['reactions'][0]['users']
                for user_i in user_id:
                    name=client._client.users_info(user=user_i)['user']['name']
                    logging.error(f"message content : {name}")
                    dict_check[text_normal[2]] = name

                # name=client._client.users_info(user=user_id)['user']['name']
                # check_f.append(name+":"+text)

                # if user_id not in id_to_user:
                #     user_name = client._client.users_info(user=user_id)['user']['name']
                #     id_to_user[user_id] = user_name

                #     user_name = id_to_user[user_id]
                # if user_name not in check_m:
                #     check_m[user_name] = 0
                #     # meetings[user_name] +=1
    except Exception as e:
        logging.error(f"Error creating conversation: {e}")   
    finally:
        return dict_check

def count_messages_reseller(seconds=24*60*60, seconds2=0):
    meetings = {}
    id_to_user = {}
    try : 
        oldest = time.time() - seconds
        # latest = time.time() - seconds2
        results = client.channel_history_iter(
            token=TOKEN,
            channel=channel_hunters, 
            oldest=oldest,
            # latest=latest
            )
        # logging.error(results)   
        # logging.error("HEERE")
        # logging.error(f"history length: {len(result['messages'])}")
        # conversation_history_weeks = result['messages']
        for message in results:
            # logging.error(f"message content : {message}")
            text = message['text'].lower()
            if "reseller" not in text:
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
@app.route('/message-count-day', methods=['POST'])
def message_count():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    hours= (datetime.datetime.today().hour)
    count_meeting_day = count_messages(seconds=hours*3600)
    tab_test=[]

    count_meeting_day=sorted(count_meeting_day.items(), key=lambda t: t[1])
    for  meet in count_meeting_day:
        tab_test.append(meet[0]+" : "+str(meet[1]))
    newList = list(reversed(tab_test))  
    newList2 = pd.DataFrame(newList,columns = ['Nb_Meeting']) 
    client.post_file(
        token=TOKEN,
        channel=channel_id,
        content=newList2,
        filename="nombre de meeting pour chaque users ce jour",
    )    
    
    return Response(), 200
@app.route('/message-count-week', methods=['POST'])
def message_count_week():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    count_meeting_week = count_messages(seconds=semaine*24*3600)
    tab_test=[]

    count_meeting_week=sorted(count_meeting_week.items(), key=lambda t: t[1])
    for  meet in count_meeting_week:
        tab_test.append(meet[0]+" : "+str(meet[1]))
    newList = list(reversed(tab_test))
    newList2 = pd.DataFrame(newList,columns = ['Nb_Meeting'])
    client.post_file(
        token=TOKEN,
        channel=channel_id,
        # content=str(newList)[1:-1],
        content=newList2,
        filename="nombre de meeting pour chaque users cette semaine",
    )
    return Response(), 200
@app.route('/message-count-last-week', methods=['POST'])
def message_count_last_week():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    last_semaine= semaine + 7
    last_time=time.time() - 4*24*3600
    count_meeting_last_week = count_messages(seconds=last_semaine*24*3600)
    tab_test=[]

    count_meeting_last_week=sorted(count_meeting_last_week.items(), key=lambda t: t[1])
    for  meet in count_meeting_last_week:
        tab_test.append(meet[0]+" : "+str(meet[1]))
    newList = list(reversed(tab_test))
    newList2 = pd.DataFrame(newList,columns = ['Nb_Meeting'])
    client.post_file(
        token=TOKEN,
        channel=channel_id,
        content=newList2,
        filename="nombre de meeting pour chaque users la semaine derniere ",
    )

    return Response(), 200
@app.route('/message-count-last-month', methods=['POST'])
def message_count_last_month():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    last_month= mois + 30
    last_time=time.time() - 250
    count_meeting_last_month = count_messages(seconds=last_month*24*3600)
    tab_test=[]

    count_meeting_last_month=sorted(count_meeting_last_month.items(), key=lambda t: t[1])
    for  meet in count_meeting_last_month:
        tab_test.append(meet[0]+" : "+str(meet[1]))
    newList = list(reversed(tab_test))
    newList2 = pd.DataFrame(newList,columns = ['Nb_Meeting'])
    client.post_file(
        token=TOKEN,
        channel=channel_id,
        content=newList2,
        filename="nombre de meeting pour chaque users le mois derniere ",
    )
   
    # response = app.response_class(
    #     response=json.dumps(count_meeting_week),
    #     mimetype='application/json'
    # )
    # return response

    return Response(), 200

@app.route('/message-count-month', methods=['POST'])
def message_count_month():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    count_meeting_month = count_messages(seconds=mois*24*3600)
    tab_test=[]

    count_meeting_month=sorted(count_meeting_month.items(), key=lambda t: t[1])
    for  meet in count_meeting_month:
        tab_test.append(meet[0]+" : "+str(meet[1]))
    newList = list(reversed(tab_test))
    newList2 = pd.DataFrame(newList,columns = ['Nb_Meeting'])
    client.post_file(
        token=TOKEN,
        channel=channel_id,
        content=newList2,
        filename="nombre de meeting pour chaque users ce mois",
        
    )
    return Response(), 200
@app.route('/reseller-month', methods=['POST'])
def reseller_month():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    reseller_month = count_messages_reseller(seconds=mois*24*3600)
    tab_test=[]

    reseller_month=sorted(reseller_month.items(), key=lambda t: t[1])
    for  meet in reseller_month:
        tab_test.append(meet[0]+" : "+str(meet[1]))
    newList = list(reversed(tab_test))
    newList2 = pd.DataFrame(newList,columns = ['Nb_Meeting'])
    client.post_file(
        token=TOKEN,
        channel=channel_id,
        content=newList2,
        filename="nombre de reseller pour chaque users ce mois",
        
    )
    return Response(), 200

@app.route('/check-month', methods=['POST'])
def check_month():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    check_month = count_check_month(seconds=mois*24*3600)
    tab_test=[]

    check_month=sorted(check_month.items(), key=lambda t: t[1])
    for  meet in check_month:
        tab_test.append(meet[1]+" : "+str(meet[0]))
    newList = list(reversed(tab_test))
    newList2 = pd.DataFrame(newList,columns = ['Nb_Meeting'])
    client.post_file(
        token=TOKEN,
        channel=channel_id,
        content=newList2,
        filename="user qui a check pour chaque meeting",
        
    )
    return Response(), 200

    

if __name__=="__main__":
    #executer sur le port 5000
    app.run(debug=True)