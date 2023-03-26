import os
import re
import time
import pyperclip
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from tqdm import tqdm
import time

load_dotenv()

# Public YouTube Data API key
API_KEY = os.getenv('API_KEY')

CHANNEL_CUSTOM_URL = os.getenv('CHANNEL_CUSTOM_URL')

# Regex pattern that matches 
# Eg, "X0X0-X0X0-X0X0-X0X0-X0X0"
PATTERN = r'([A-Z0-9]{4,5}-){4}[A-Z0-9]{4,5}'

# Authenticate API
def get_authenticated_service():
    return build('youtube', 'v3', developerKey=API_KEY)

# Get Channel ID from custom YouTube URL
# Eg, "https://youtube.com/c/overwatchleague"
def get_channel_id(youtube, custom_url):
    custom_url = custom_url.split("/")[-1]
    response = youtube.search().list(
        part='snippet',
        type='channel',
        q=custom_url,
        maxResults=1
    ).execute()

    return response['items'][0]['snippet']['channelId'] if response['items'] else None

# Check if channel is live 
# Return live stream video ID if response is populated 
def get_active_live_video_id(youtube, channel_id):
    response = youtube.search().list(
        part='id',
        channelId=channel_id,
        eventType='live',
        type='video',
        maxResults=1
    ).execute()

    return response['items'][0]['id']['videoId'] if response['items'] else None

# Get chat ID for live stream with video ID
def get_live_chat_id(youtube, video_id):
    response = youtube.videos().list(
        part='liveStreamingDetails',
        id=video_id
    ).execute()

    live_chat_id = response['items'][0]['liveStreamingDetails']['activeLiveChatId']
    return live_chat_id

# Get 200 most recent live chat messages
def get_chat_messages(youtube, live_chat_id, page_token=None):
    response = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part='id,snippet',
        maxResults=200,
        pageToken=page_token
    ).execute()

    return response

# def play_notification_sound():
#     sound_file = "notification_sound.mp3"  # Replace this with the path to your sound file
#     playsound(sound_file)

# Iterate over each message, checking if regex pattern is found
# If found, return the message and copy to clipboard
def process_messages(messages, pattern):
    for message in messages:
        text = message['snippet']['textMessageDetails']['messageText']
        match = re.search(pattern, text)
        if match:
            print(f"Found matching message: {text}")
            pyperclip.copy(match.group())
            # play_notification_sound()

# playing around with graphical solutions; temporary
def wait_with_progress(polling_interval):
    for _ in tqdm(range(polling_interval), desc="Waiting", unit="ms", ncols=80):
        time.sleep(1/1000)
        

def main():
    youtube = get_authenticated_service()
    channel_id = get_channel_id(youtube, CHANNEL_CUSTOM_URL)

    if not channel_id:
        print(f"Could not find channel with custom URL '{CHANNEL_CUSTOM_URL}'")
        return

    video_id = get_active_live_video_id(youtube, channel_id)

    if not video_id:
        print(f"No active live stream found for channel '{CHANNEL_CUSTOM_URL}'")
        return

    live_chat_id = get_live_chat_id(youtube, video_id)
    pattern = re.compile(PATTERN)

    next_page_token = None
    while True:
        try:
            response = get_chat_messages(youtube, live_chat_id, next_page_token)
            process_messages(response['items'], pattern)

            next_page_token = response['nextPageToken']
            polling_interval = response['pollingIntervalMillis']

            wait_with_progress(polling_interval)
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
            break

if __name__ == '__main__':
    main()