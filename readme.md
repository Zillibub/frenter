# Frenter

Frenter is a friend who will help you to rent. 

I'm moving to London, so I decided to create a small scrapper to make by flat search for rent a bit convenient. 

Pipeline: 
1. Check for new listings every n seconds
2. Filter them by price, amount of beds, zone
3. Map crime rate and other metadata  by zip code
4. Send a report with the url to the messenger

Sample bot response: 

![Sample](docs/images/example.png)

# Quick start

For now start is a bit tricky, I created it mostly for myself, so you'll 
need to perform some dev-like actions.

### Step 0. Clone this repo
```commandline
git clone https://github.com/Zillibub/frenter.git
```

Execute the commands below inside the downloaded folder

### Step 1. create virtual env and install dependencies

```commandline
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2. download postcodes dataset

The first thing to do - download [London postcodes dataset](https://data.london.gov.uk/download/postcode-directory-for-london/62b22f3f-25c5-4dd0-a9eb-06e2d8681ef1/london_postcodes-ons-postcodes-directory-feb22.csv) 
from this url to `data` folder. For example, you can execute this command inside the folder:
```commandline
mkdir data
wget -P data https://data.london.gov.uk/download/postcode-directory-for-london/62b22f3f-25c5-4dd0-a9eb-06e2d8681ef1/london_postcodes-ons-postcodes-directory-feb22.csv
```

### Step 3. Create your telegram bot

Go to [@BotFather](https://t.me/BotFather) in telegram and follow its instructions. 

You'll get a `TELEGRAM_BOT_TOKEN` which is required to start this app.

### Step 4. Get your chat id 

The easiest way to get the chat ID is to ask [@RawDataBot](https://t.me/RawDataBot) to return it by pressing `/start`.

You'll get something like that: 
```
{'ok': True,
'result': [{'update_id': <some number>,
 'message': {'message_id': 2,
  'from': {'id': <this is the value you need>,
   'is_bot': False,
   'first_name': '<first name>',
   'last_name': '<last name>',
   'username': '<username>',
   'language_code': 'en'},
  'chat': {'id': <this is the value you need>,
   'first_name': '<first name>',
   'last_name': '<last name>',
   'username': '<username>',
   'type': 'private'},
  'date': <date>,
  'text': 'd'}}]}
```
You need `response['chat']['id']` value, this is your `TELEGRAM_CHAT_ID`
   

### Step 5. Create `.env` file with following content
    ```
    TELEGRAM_BOT_TOKEN = '<your bot token>'
    TELEGRAM_CHAT_ID = <your chat id>
    ```

### Step 6. Change search parameters if you want in `main.py`


### Step 7. Start script with 
```commandline
PYTHONPATH=src python main.py
```