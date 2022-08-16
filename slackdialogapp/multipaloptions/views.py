from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
import slack
import json
from urllib import parse

@csrf_exempt
def message_options(request):
	s = request.body.decode('utf-8')
	unquoted=parse.unquote(s).replace("payload=","")
	json_dump = json.loads(unquoted)
	client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)
	if json_dump["callback_id"] == "menu_options_2319":
		menu_options={
		"options": [
		{
		"text": "Hot",
		"value": "hot"
		},
		{
		"text": "Cold",
		"value": "cold"
		}
		]
		}
	elif json_dump["callback_id"] == "menu_options_23191":
		menu_options = {
			"options": [
				{
				"text": "Cappuccino",
				"value": "cappuccino"
				},
				{
				"text": "Latte",
				"value": "latte"
				}
			]
		}
	elif json_dump["callback_id"] == "menu_options_23192":
		menu_options = {
			"options": [
				{
				"text": "Coca cola",
				"value": "coca_cola"
				},
				{
				"text": "Dew",
				"value": "dew"
				}
			]
		}
	return HttpResponse(json.dumps(menu_options), content_type='application/json')


@csrf_exempt
def message_actions(request):
	client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)
	s = request.body.decode('utf-8')
	unquoted=parse.unquote(s).replace("payload=","")
	json_dump = json.loads(unquoted)
	print(json_dump)
	selection = json_dump['actions'][0]['selected_options'][0]['value']
	callback_id = json_dump["callback_id"]
	if selection == "hot":
		attachments_json = [
		    {
		        "fallback": "Upgrade your Slack client to use messages like these.",
		        "color": "#3AA3E3",
		        "attachment_type": "default",
		        "callback_id": "menu_options_23191",
		        "actions": [
		            {
		                "name": "bev_list",
		                "text": "Pick a beverage...",
		                "type": "select",
		                "data_source": "external"
		            }
		        ]
		    }
		]
		# Send a message with the above attachment, asking the user if they want coffee
		client.chat_postMessage(
		  channel="C01FSBWU7CN",
		  text="",
		  attachments=attachments_json
		)
	elif selection == "cold":
		attachments_json = [
		    {
		        "fallback": "Upgrade your Slack client to use messages like these.",
		        "color": "#3AA3E3",
		        "attachment_type": "default",
		        "callback_id": "menu_options_23192",
		        "actions": [
		            {
		                "name": "bev_list",
		                "text": "Pick a beverage...",
		                "type": "select",
		                "data_source": "external"
		            }
		        ]
		    }
		]
		# Send a message with the above attachment, asking the user if they want coffee
		client.chat_postMessage(
		  channel="C01FSBWU7CN",
		  text="",
		  attachments=attachments_json
		)
		

	response = client.chat_update(channel=json_dump["channel"]["id"],
      ts=json_dump["message_ts"],
      text="You have Selected {}!".format(selection),
      attachments=[])
	return HttpResponse(status=200)