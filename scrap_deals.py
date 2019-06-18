from bs4 import BeautifulSoup
import requests
import json
import logging
import tweepy
import urllib.request
import random


ct=0
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter_ui = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
fh = logging.FileHandler(f'logs_twitter.txt')
fh.setFormatter(formatter)
fh.setLevel(logging.INFO)
logger.addHandler(fh)

###credentials
with open('twitter_conf') as json_file:
    data = json.load(json_file)
consumer_key = data['consumer_key']
consumer_secret = data['consumer_secret']
access_token = data['access_token']
access_token_secret = data['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
###download the image, local, push it , and delete it after

def downloader(image_url):
    file_name = random.randrange(1,10000)
    full_file_name = str(file_name) + '.jpg'
    try:
        urllib.request.urlretrieve(image_url, 'img.png')
    except urllib.error.HTTPError:
        image_url = "http://etl-games.co.uk/Awaiting-Image.jpg"
        urllib.request.urlretrieve(image_url, 'img.png')
    return full_file_name



###update the state of the deals pushed
def update_deals(dict_connections):
    try:
        with open('state_deals.json') as json_file:
            data = json.load(json_file)

        data.extend([dict_connections])
        with open('state_deals.json', 'w') as fp:
            json.dump(data if type(data) is list else [data], fp)
        logger.info('deal Information stored...')
    except IOError:
        logger.info('Creation of state....')
        with open('state_deals.json', 'w') as fp:
            json.dump(dict_connections if type(dict_connections) is list else [dict_connections], fp)

def check_state(deal):
    try:
        tmp = open('state_deals.json').read()
        tt = tmp.replace(u"\\u00c2","").replace(u"\\u00a0","")
        tt = tt.replace(u"\\u00a","")
        tt = tt.replace(u"\\u00a3","£")
        tt = tt.replace(u'\\u2018','')
        tt = tt.replace(u'\\u2019','')
        deal = deal.replace(u'\xa0','')
        if deal in tt:
            return True
        else:
            return False
    except FileNotFoundError:
        pass

def add_hash(deal):
    deal = deal.replace("Nintendo","#Nintendo")
    deal = deal.replace("Switch","#Switch")
    deal = deal.replace("PS4","#PS4")
    deal = deal.replace("PS3","#PS3")
    deal = deal.replace("Xbox","#Xbox")
    deal = deal.replace("Steam","#Steam")
    deal = deal.replace("PC","#PC")
    deal = deal.replace("PSN","#PSN")
    deal = deal + " #GameDeal"
    return deal



if __name__ == '__main__':
    URL = 'gaming-new'
    #content = requests.get(URL)
    soup = BeautifulSoup(open(URL), 'html.parser')
    rows = soup.find_all('article')
    for row in rows[1:]:          # Print all occurrences
        try:
            data_descri = row.find_all('a', href=True)[1]
            data_url = row.find_all('a', href=True)[5]
            print(data_url["href"])
            if "comments" in data_url["href"]:
                data_url = row.find_all('a', href=True)[3]
                print(f'replaced with {data_url["href"]}')
            img = row.find_all('img')
            deal = data_descri.text.replace('\n\t','')
            url = requests.get(data_url["href"]).url
            tmp_dict = {"deal": deal,"url":url}
            if not('hotukdeals') in url:
                if not(check_state(deal)):
                    deal = add_hash(deal)
                    tweet = f'{deal}({url})'
                    if img[0].has_attr('src'):
                        to_download = img[0]['src']
                    else:
                        to_download = json.loads(img[0]['data-lazy-img'])['src']
                    image_path = downloader(to_download)
                    try:
                        status = api.update_with_media("img.png", tweet)
                    except tweepy.error.TweepError:
                        api.update_status(tweet)
                    #os.remove("img.png")
                    update_deals(tmp_dict)
                    logger.info(f'{deal} pushed')
                else:
                    logger.info(f'{deal} already pushed')
            else:
                print("hotukdeals url founded")
        except IndexError:
            pass
        except KeyError:
            pass

