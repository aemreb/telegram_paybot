import logging
import enum
import psycopg2
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()


class Status(enum.Enum):
    Initial = 0
    SignUpMail = 1
    SignUpPassword = 2
    SignUpSuccessful = 3
    LoginMail = 4
    LoginPassword = 5
    LoginSuccessful = 6
    LoginFailed = 7

status = Status(Status.Initial)
logger = logging.getLogger(__name__)
TOKEN = '1624315620:AAH5Ol2MORB80I6ArA6WwVBIAAcSranNAAk'

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def echo(update, context):
    """Echo the user message."""
    global status
    if status == Status.SignUpMail:
        update.message.reply_text("Enter your password: ")
        status = Status.SignUpPassword
    elif status == Status.SignUpPassword:
        update.message.reply_text("Enter your password: ")
        finishSignup()
        status = Status.SignUpSuccessful
    else:
        print(status)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def signup(update, context):
    userID = update.message.from_user.id
    print(userID)
    cur.execute("INSERT INTO users (userID, money) VALUES (%s, %s)",
                (userID, 50.0))

    print(cur.fetchall())

    conn.commit()


def finishSignup():
    print("")
def main():

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    updater = Updater(TOKEN, use_context=True)
    cur.execute("""
    SELECT * 
    FROM users
""")
    print(cur.fetchall())

    # close the communication with the HerokuPostgres
    cur.close()

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("signup", signup))


    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://protected-mesa-20804.herokuapp.com/' + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()



if __name__ == '__main__':
    main()