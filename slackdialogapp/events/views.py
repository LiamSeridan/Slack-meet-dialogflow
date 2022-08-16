from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from django.http import HttpResponse, JsonResponse
import slack
import os
from google.cloud import dialogflow
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.api_core.exceptions import InvalidArgument
from time import sleep
from colorama import Fore

from .models import slackuser,dialogflowintent

@csrf_exempt
def event_hook(request):
	client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)
	json_dict = json.loads(request.body.decode('utf-8'))
	if json_dict['token'] != settings.VERIFICATION_TOKEN:
		return HttpResponse(status=403)
	if 'type' in json_dict:
		if json_dict['type'] == 'url_verification':
			response_dict = {"challenge": json_dict['challenge']}
			return JsonResponse(response_dict, safe=False)
	if 'event' in json_dict:
		event_msg = json_dict['event']
		if ('subtype' in event_msg) and (event_msg['subtype'] == 'bot_message'):
			return HttpResponse(status=200)
		if ('subtype' in event_msg) and (event_msg['subtype'] == 'message_changed'):
			return HttpResponse(status=200)
	if event_msg['type'] == 'message' and event_msg.get('channel') == "C01FSBWU7CN":
		send_message(client, event_msg)
		return HttpResponse(status=200)
	return HttpResponse(status=200)



def send_message(client, event_msg):
	BOT_ID = client.api_call("auth.test")['user_id']
	user = event_msg.get('user')
	channel_id = event_msg.get('channel')


	if user != BOT_ID and is_trainer(client, user,event_msg) and user is not None:
		channel_id = event_msg.get('channel')
		ts = event_msg.get('thread_ts')
		if ts is None:
			ts = event_msg.get('ts')

		text_to_be_analyzed = clean_text_for_dialog(event_msg.get('text'))
		if len(text_to_be_analyzed) >= 255:
			print(Fore.YELLOW + "Text length is more than 255")
			print(Fore.YELLOW + text_to_be_analyzed)
			client.chat_postMessage(channel=channel_id, thread_ts=ts, text="<@U01HYKL9WTA> <@U01H90W4CAF> <@U022JE37412> <@U02CPS6KQFJ> Need help resolving query of <@"+str(user)+">")
		else:
			os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'private_key.json'
			DIALOGFLOW_PROJECT_ID = 'zoomslack'
			DIALOGFLOW_LANGUAGE_CODE = 'en'
			SESSION_ID = user

			session_client = dialogflow.SessionsClient()
			session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)
			text_input = dialogflow.TextInput(text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
			query_input = dialogflow.QueryInput(text=text_input)
			try:
				response = session_client.detect_intent(session=session, query_input=query_input)
				print(response)
			except Exception as e:
				print(Fore.RED + str(e))
				print(Fore.RED + text_to_be_analyzed)

			try:
				dialogflowintents = dialogflowintent.objects.filter(intentName=response.query_result.intent.display_name.lower()).first()
				if dialogflowintents.accuracy <=  response.query_result.intent_detection_confidence:
					print(Fore.GREEN + "Dialog flow accuracy:- " + str(response.query_result.intent_detection_confidence))
					print(Fore.GREEN + "Intent name:- " + response.query_result.intent.display_name)
					print(Fore.GREEN + "Threshold:- " + str(dialogflowintents.accuracy))
					client.chat_postMessage(channel=channel_id, thread_ts=ts, text="<@"+str(user)+"> "+response.query_result.fulfillment_text)
				else:
					print(Fore.YELLOW + "Dialog flow accuracy:- " + str(response.query_result.intent_detection_confidence))
					print(Fore.YELLOW + "Intent name:- " + response.query_result.intent.display_name)
					print(Fore.YELLOW + "Threshold:- " + str(dialogflowintents.accuracy))
					client.chat_postMessage(channel=channel_id, thread_ts=ts, text="<@U01HYKL9WTA> <@U01H90W4CAF> <@U022JE37412> <@U02CPS6KQFJ> Need help resolving query of <@"+str(user)+">")
			except Exception as e:
				print(Fore.RED + str(e))
				print(Fore.RED + text_to_be_analyzed)
				print(Fore.RED + str(response))
				client.chat_postMessage(channel=channel_id, thread_ts=ts, text="<@U01HYKL9WTA> <@U01H90W4CAF> <@U022JE37412> <@U02CPS6KQFJ> Need help resolving query of <@"+str(user)+">")
			


def is_trainer(client, userId, event_msg):
	slackuser_object = slackuser.objects.filter(slackuseID=userId).first()
	try:
		return slackuser_object.is_restricted
	except Exception as e:
		if get_slack_user(client):
			slackuser_object = slackuser.objects.filter(slackuseID=userId).first()
			try:
				return slackuser_object.is_restricted
			except Exception as e:
				print(Fore.RED + "Second Exception")
				return 1
		print(Fore.RED + str(e))
		print(Fore.RED + userId)
		print(Fore.RED + str(event_msg))
		print()
		print()
		print(Fore.RED + "Not found trainer......")
		return 1

def clean_text_for_dialog(s):
	while "<@" in s:
		s = s[:s.find("<@")].strip() + " " + s[s.find(">")+1:].strip()
	return s.strip()

def get_slack_user(client):
	slackuser.objects.all().delete()
	next_cursor ='xyz'
	while next_cursor:
	    result = ''
	    if next_cursor == 'xyz':
	        result = client.users_list()
	    else:
	        result = client.users_list(cursor=next_cursor)
	        
	    next_cursor = result['response_metadata']['next_cursor']
	    save_users(result["members"])
	return True

def save_users(users_array):
    for user in users_array:
        if user["deleted"] == False :
        	s= slackuser(slackuseID=user.get("id"),teamID=user.get("team_id"),real_name=user.get("real_name"),is_admin=user.get("is_admin"),is_owner=user.get("is_owner"),is_primary_owner=user.get("is_primary_owner"),is_restricted=user.get("is_restricted"),is_ultra_restricted=user.get("is_ultra_restricted"),is_deleted=user.get("deleted"),is_bot=user.get("is_bot"))
        	s.save()


def update_table(client, text, channel_id, user_id):
	if text == "dialogflow":
		client.chat_postEphemeral(channel=channel_id,user =user_id, text="Started dialogflowintent saving")
		dialogflowintent.objects.all().delete()
		GOOGLE_CONFIGURATION_SHEET = ""#TODO:- Google Sheet ID where all intent name and a deafult values set
		#accessing the Sheet credentials
		SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
		SERVICE_ACCOUNT_FILE = 'private_key.json'
		credentials = None
		credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
		service = build('sheets', 'v4', credentials=credentials)
		sheet = service.spreadsheets()

		#geeting all agents and filttering active agents only
		result = sheet.values().get(spreadsheetId=GOOGLE_CONFIGURATION_SHEET, range="").execute()#TODO:- Sheet range for Intents of Dialogflowc

		#list of all the agents
		values = result.get('values', [])

		
		for l in values:
			if l[0] != "Intent Name":
			    dialogflowintents = dialogflowintent(intentName= l[0].lower(), accuracy = l[1])
			    dialogflowintents.save()
		client.chat_postEphemeral(channel=channel_id,user =user_id, text="Dialogflowintent saved all")
	elif text == "slackuser":
		client.chat_postEphemeral(channel=channel_id,user =user_id, text="Started slackuser saving")
		get_slack_user(client)
		client.chat_postEphemeral(channel=channel_id,user =user_id, text="Slackuser saved all")

	elif text == "help":
		# A Dictionary of message attachment options
		attachments_json = [
		    {
		        "fallback": "Upgrade your Slack client to use messages like these.",
		        "color": "#3AA3E3",
		        "attachment_type": "default",
		        "callback_id": "menu_options_2319",
		        "actions": [
		            {
		                "name": "bev_list_type",
		                "text": "Pick a type...",
		                "type": "select",
		                "data_source": "external"
		            }
		        ]
		    }
		]
		# Send a message with the above attachment, asking the user if they want coffee
		client.chat_postMessage(
		  channel="C01FSBWU7CN",
		  text="Would you like some drink?",
		  attachments=attachments_json
		)

@csrf_exempt
def event_slash(payload):
	data =str(payload.body)
	user_id = data[data.find("&user_id=")+9:data.find("&user_id=")+data[data.find("&user_id=")+1:].find("&")+1] 
	text = data[data.find("&text=")+6:data.find("&text=")+data[data.find("&text=")+1:].find("&")+1]
	channel_id = data[data.find("&channel_id=")+12:data.find("&channel_id=")+data[data.find("&channel_id=")+1:].find("&")+1]

	client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)

	if user_id == "UMTQJ7ETE":
		update_table(client, text, channel_id, user_id)
	else:
		client.chat_postEphemeral(channel=channel_id,user =user_id, text="You are not allowed to do so")
	return HttpResponse(status=200)