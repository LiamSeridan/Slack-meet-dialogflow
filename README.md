# Slack-meet-dialogflow
This Project is created for chatbot for slack using Dialogflow, Python, Django

Slack(new Message)-->Python(Django)-->Dialogflow-->Python(Django)-->Slack(Post Message)

TODO:- Items to do 

slackdialogapp/slackdialogapp/settings.py
Add Following Token to file
1. SECRET_KEY
2. VERIFICATION_TOKEN
3. OAUTH_ACCESS_TOKEN
4. BOT_USER_ACCESS_TOKEN
5. CLIENT_ID
6. CLIENT_SECRET

Add Google Json key to access Google sheet and Dialogflow in Folder slackdialogapp(REF):- https://github.com/gour6380/Python-Google-sheet

slackdialogapp/events/views.py
Add Google Sheet ID and Google Range
1. GOOGLE_CONFIGURATION_SHEET
2. range(line no.:- 154)

For Accessing Slack Token:- https://api.slack.com/authentication/token-types

Also A database is added where we are storing the details of slack users to check for which user we should reply and for which we shouldn't.
Also added a feature for Dropdown select in mutipaldrop down as Django as Backend

Once you Run the Project It will give you a Url add that to ngrok to get a URL for Slack to update the Endpoints
