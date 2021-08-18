from telegram.ext import *
import requests
from bs4 import BeautifulSoup as soup
import json
import re
from datetime import datetime
import os
import logging
import nlp

current_dt = datetime.now().date()

# loading the config file with all sensitive info stored
with open('config.json','r') as f:
    config_data = json.load(f)

# defined start command
def start_command(update,context):
    update.message.reply_text('Hi, Welcome to the Lambton College!\nMy name is Cherry. How may I help you?')

# response command to act on messages
def response(update,context):

    msg = update.message.text
    ints = nlp.predict_class(msg)
    res = nlp.get_response(ints, nlp.intents)

    # logging into moodle
    def loginMoodle():
        session = requests.session()
        moodle_login_source = session.get(config_data['moodle_login_page'],verify = 'cacert.pem')
        moodle_login_soup = soup(moodle_login_source.content,'html.parser')
        logintoken = moodle_login_soup.find('input',{'name':'logintoken'})
        config_data['payload'].update({'logintoken' : logintoken['value']})

        session.post(url=config_data['moodle_login_page'],data=config_data['payload'],headers=config_data['moodle_login_page_headers'],verify='cacert.pem')
        return session

    # cleaning and extracting date
    def processDt(dt):
        dt_ls = dt.split(',')
        return datetime.strptime(dt_ls[1],' %d %B %Y').date()

    # extracting the data of the post
    def extractData(e):
        h = e.find('div',{'class':'topic firstpost starter'}).text
        last_sign = h[::-1].index('-')
        from_start = len(h) - last_sign
        processed_h,dt = h[:(from_start-2)],h[from_start+1:]
        processed_h = re.sub('by',' by',processed_h).strip()
        processed_dt = processDt(dt)
        if processed_dt == current_dt:
            content = e.find('div',{'class':'content'}).text
            processed_content = re.sub('[\xa0\\n]','',content)
            imgs = e.find('div',{'class':'content'}).findAll('img')
            imgs_src = []
            if len(imgs) !=0:
                for im in imgs:
                    imgs_src.append(im['src'])
            return processed_h,processed_content,imgs_src
        else:
            return None

    # extracting the subject for which assignment is submitted
    def extractAssignmentHeader(session,link):
        activity_link = session.get(link)
        activity_soup = soup(activity_link.content,'html.parser')
        return activity_soup.find('div',{'class' : 'page-header-headings'}).text

    if res == 'Site News':
        todays_update = []

        session = loginMoodle()
        moodle_loggedin_source = session.get(config_data['moodle_page'])

        session.close()

        moodle_loggedin_soup = soup(moodle_loggedin_source.content,'html.parser')
        moodle_loggedin_soup.find('div',{'class' : 'logininfo'})

        site_news = moodle_loggedin_soup.find('div',{'id':'site-news-forum'})
        posts = site_news.findAll('div',{'class':'forumpost clearfix firstpost starter'})


        for e in posts:
            ls = extractData(e)
            if ls is not None:
                todays_update.append(ls)

        s = ''

        for idx,up in enumerate(todays_update,1):
            s += '## Post ' + str(idx) + ') ##\n\n'
            for sp in up:
                if len(sp) !=0:
                    if type(sp) is list:
                        for im in sp:
                            s += im
                            s += '\n\n'
                    else:
                        s += sp
                    s += '\n\n'
            s += '\n'

        if s.strip() == '':
            s = 'No Posts for today found.'

        update.message.reply_text(s.strip())


    elif res == 'Due Assignments':

        session = loginMoodle()
        moodle_upcoming_source = session.get(config_data['moodle_upcoming_page'])

        moodle_upcoming_soup = soup(moodle_upcoming_source.content, 'html.parser')
        upcoming_assignment = moodle_upcoming_soup.find_all('div', class_ = 'event')
        upcoming_assignment[0].findAll('a')
        
        activity_content = []

        for task in upcoming_assignment:
            for a_href in task.findAll('a'):
                if a_href.text == 'Go to activity':
                    activity_header = extractAssignmentHeader(session,a_href['href'])
                    activity_content.append(activity_header + '\n' + task.text.strip() + '\n' + a_href['href'])

        s = ''

        for idx,ac in enumerate(activity_content,1):
            s += '\n' + '## Task ' + str(idx) + ') ##\n\n'
            s += ac + '\n'

        if s.strip() == '':
            s = 'No Pending Assignments found.'
        
        session.close()
        
        return update.message.reply_text(s.strip())
    
    else:
        update.message.reply_text(res)

def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

    logger = logging.getLogger(__name__)

    updater = Updater(config_data['tele_bot_token'],use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start',start_command))
    dp.add_handler(MessageHandler(Filters.text,response))
    PORT = int(os.environ.get('PORT',5000))
    updater.start_webhook(listen='0.0.0.0',port=PORT,url_path=config_data['tele_bot_token'],webhook_url= config_data['heroku_app']  + config_data['tele_bot_token'])
    updater.idle()


if __name__ == '__main__':
    main()
