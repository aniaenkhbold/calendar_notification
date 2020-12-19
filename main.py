"""
By: Ariunzaya Enkhbold
Credits to: Twilio API samples, Google Calendar API samples

The purpose of this program is to utilize the free trials of twilio messaging API and Google Calendar API
to create a program that sends daily automated messages to the user. The message contains the user's
schedule for the day stored in their Google Calendar. This specific code only works with Ariunzaya's google
calendar and phone number but it can be further enhanced to be compatible with any user who grants access
and authentication.

"""

from __future__ import print_function
import datetime
import pickle
import os.path
import schedule
import time

from credential_tokens import user_number, twilio_number, user_sid, user_token

from datetime import timedelta

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from twilio.rest import Client

SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    """Uses the twilio messaging API to send messages to the user's number.
    Authentication is below.
    """
    # Your Account SID from twilio.com/console
    account_sid = user_sid
    # Your Auth Token from twilio.com/console
    auth_token = user_token

    client = Client(account_sid, auth_token)

    """Uses Google Calendar API to access the user's detailed schedules on google calendar.
    Authentication is below.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)


    service = build('calendar', 'v3', credentials=creds)


    """Function that sends the user's schedule for that day
    Calls the calendar API and twilio messaging API as well as schedule library
    """
    def send_schedule():

        #matches the value of timeMin and timeMax to the current date
        print(datetime.date.day)

        #time at the time the function is called timeMin
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print(now)

        #time 24 hours from the time the function is called timeMax
        tomorrow = (datetime.datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'
        print(tomorrow)

        print('Getting the schedule for the next 24 hours')
        events_result = service.events().list(calendarId='primary', timeMin=now ,timeMax = tomorrow,
                                        singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])


        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

            message = client.messages.create(
                to=user_number,
                from_=twilio_number,
                body=start + event['summary'])
        print(message.sid)

    #  Automated to send every day at 7:00 a.m.
    schedule.every().day.at("18:40").do(send_schedule)



if __name__ == '__main__':
    main()

#Checks whether the scheduled function is working
while True:
    # Checks whether a scheduled task
    # is pending to run or not
    schedule.run_pending()

    time.sleep(2)
    print("its been 2 seconds?")





