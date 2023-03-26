# OWL-Token-Bot
A simple, unorganized semi-automatic bot that scrapes redeemable codes in OWL live chat giveaways (battle.net/code).

# Limitations
I scrambled this together while watching the OWL2023 Pro-Am series on YouTube Live, forgetting `pyautogui` doesn't work easily with WSL2/Windows. As a result, the process of actually reedeming the code is manual, so you have to be quick.

# Install
1. Install Python >3 (project used Python 3.10)
2. Clone the repo
3. `cd ./owl-token-copier`
4. `pip install google-api-python-client google-auth-httplib2 pyperclip tqdm python-dotenv`
5. python main.py