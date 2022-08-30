# Frenter

Frenter is a friend who will help you to rent. 

I'm moving to London, so I decided to create a small scrapper to make by flat search for rent a bit convenient. 

Pipeline: 
1. Check for new listings every n seconds
2. Filter them by price, amount of beds, zone
3. Map crime rate and other metadata  by zip code
4. Send a report with the url to the messenger

# Quick start

The first thing to do - download [London postcodes dataset](https://data.london.gov.uk/download/postcode-directory-for-london/62b22f3f-25c5-4dd0-a9eb-06e2d8681ef1/london_postcodes-ons-postcodes-directory-feb22.csv) 
from this url to data folder.

Then you'll need a python and a created telegram bot

