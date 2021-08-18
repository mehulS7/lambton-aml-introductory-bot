# Lambton AIML Introductory Bot
- **Developers ([Anaekh Dheepak](https://github.com/anaekhdheepak) , Mehul Sachdeva)**

### Please go to your Telegram app and search for @lookup_bot with name BotMan. Start using...

## Custom Build
> Stage 1) Create your own Telegram Bot
- Go to telegram and search for BotFather
- Run the command /newbot and follow the instructions
- Replace the token received in the config file

Reference [https://sendpulse.com/knowledge-base/chatbot/create-telegram-chatbot]


> Stage 2) Deploy your code in Heroku
- Register on [heroku](https://signup.heroku.com/dc)
- Download [CLI](https://devcenter.heroku.com/articles/getting-started-with-python#set-up)
- Create an app
- Use the app username and place it in the config file
- Initialize the git in the same folder and commit your files
- Make sure the Heroku CLI is added to your system path
- Go to the path where project is present on Terminal
- Run folowing commands
  - heroku login
  - heroku git:remote -a YourAppName
  - git push heroku master
  
Reference [https://towardsdatascience.com/how-to-deploy-a-telegram-bot-using-heroku-for-free-9436f89575d2]
 
**Note:** If you don't want to publish the code on a server. Please comment the folowing code from the bot.py file

    # PORT = int(os.environ.get('PORT',8443))
    # updater.start_webhook(listen='0.0.0.0',port=PORT,url_path=config_data['tele_bot_token'],webhook_url= config_data['heroku_app'] + config_data['tele_bot_token'])
    # updater.idle()
   
AND, include the below and run

    # updater.start_polling()

> Stage 3) Place your Moodle username and password in the config.json file
