import logging
import psycopg2
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
conn.autocommit = False
cur = conn.cursor()

logger = logging.getLogger(__name__)
TOKEN = '1624315620:AAH5Ol2MORB80I6ArA6WwVBIAAcSranNAAk'

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! Type /signup to sign up.')

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text('Unknown command. Type /help to see the help menu.')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def signup(update, context):
    userID = update.message.from_user.id
    print(userID)
    try:
        print(update.message.text.split())
        username = update.message.text.split()[1]
        cur.execute("INSERT INTO users (userID, money, username) VALUES (%s, %s, %s)",
                (userID, 50.0, username))
        update.message.reply_text("Created user. Welcome to Paybot.")
    except Exception as error:
        print(error)

    cur.execute("""
        SELECT * 
        FROM users 
    """)
    print(cur.fetchall())

    conn.commit()

def atm(update, context):
    try:
        cur.execute("SELECT money FROM users WHERE userID = %s",
                    (str(update.message.from_user.id), ))

        update.message.reply_text("You have " + str(cur.fetchone()[0]) + " buxx 🤑")
    except Exception as error:
        print(error)

def send(update, context):
    sender = update.message.from_user.id
    print(sender)
    receiver_username = update.message.text.split()[1]
    print(receiver_username)
    amount = update.message.text.split()[2]
    print(amount)
    exchange()

    try:
        cur.execute("SELECT userID FROM users WHERE username = %s",
                    (receiver_username, ))
        print(cur.fetchone()[0])
        if cur.fetchone():
            receiver = cur.fetchone()[0]
            print(receiver)


        else:
            pass
    except Exception as error:
        print(error)

    conn.commit()

def exchange():
    try:
        print("Contents of the Employee table: ")
        sql = '''SELECT * from users'''
        cur.execute(sql)
        print(cur.fetchall())

        # Updating the records
        sql = "UPDATE users SET money = money + %s WHERE userID = '%s'"
        cur.execute(sql, (10, "1234567"))
        print("Table updated...... ")

        conn.commit()
        cur.close()
    except Exception as error:
        print(error)


def main():

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    updater = Updater(TOKEN, use_context=True)

    # close the communication with the HerokuPostgres

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("signup", signup))
    dp.add_handler(CommandHandler("atm", atm))
    dp.add_handler(CommandHandler("send", send))

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