import logging
import psycopg2
from telegram.ext import Updater, CommandHandler
import os

import strings

PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.getenv("API_KEY", "optional-default")
PROJECT_URL = os.getenv("PROJECT_URL", "optional-default")
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
conn.autocommit = True
cur = conn.cursor()

logger = logging.getLogger(__name__)


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text(strings.signup)


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(strings.help)


def signup(update, context):
    cur = conn.cursor()
    userID = update.message.from_user.id
    try:
        print(update.message.text.split())
        username = update.message.text.split()[1]
        cur.execute(
            "INSERT INTO users (userID, money, username) VALUES (%s, %s, %s)",
            (userID,
             50.0,
             username))
        update.message.reply_text(strings.user_created)
    except Exception as error:
        update.message.reply_text(strings.user_exists)
        print(error)

    conn.commit()
    cur.close()


def atm(update, context):
    cur = conn.cursor()
    try:
        cur.execute("SELECT money FROM users WHERE userID = %s",
                    (str(update.message.from_user.id),))

        update.message.reply_text(
            "You have " + str(cur.fetchone()[0]) + " buxx 🤑")
    except Exception as error:
        print(error)

    conn.commit()
    cur.close()


def send(update, context):
    cur = conn.cursor()
    sender = update.message.from_user.id
    receiver_username = update.message.text.split()[1]
    amount = update.message.text.split()[2]

    try:
        cur.execute("SELECT userID FROM users WHERE username = %s",
                    (receiver_username,))
        receiver = cur.fetchone()[0]
        exchange(update, amount, receiver_username, str(receiver), str(sender))

    except Exception as error:
        print(error)

    conn.commit()
    cur.close()

def whoami(update, context):
    cur = conn.cursor()
    sender = update.message.from_user.id

    try:
        cur.execute("SELECT username FROM users WHERE userID = %s",
                    (sender,))
        receiver = cur.fetchone()[0]

        update.message.reply_text("Your username is " + receiver)

    except Exception as error:
        print(error)

    conn.commit()
    cur.close()

def exchange(update, amount, receiver_username, receiver, sender):
    cur = conn.cursor()

    try:
        sql = '''SELECT * from users'''
        cur.execute(sql)
        result_set = cur.fetchall()
        shouldTransfer = False
        for row in result_set:
            if row[0] == sender and row[1] >= int(amount) and int(amount) > 0:
                shouldTransfer = True

        if shouldTransfer:
            sql = "UPDATE users SET money = money + %s WHERE userID = %s"
            cur.execute(sql, (amount, receiver))

            sql = "UPDATE users SET money = money - %s WHERE userID = %s"
            cur.execute(sql, (amount, sender))

            sql = "SELECT username FROM users WHERE userID = %s"
            cur.execute(sql, (sender,))
            sender_username = cur.fetchone()[0]
            update.message.reply_text(
                str(amount) +
                " buxx sent to " +
                str(receiver_username) +
                " by " +
                str(sender_username) +
                " 😫")
        else:
            update.message.reply_text(strings.not_enough_buxx)

            conn.commit()
            cur.close()
    except Exception as error:
        print(error)


def main():

    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("signup", signup))
    dp.add_handler(CommandHandler("atm", atm))
    dp.add_handler(CommandHandler("send", send))
    dp.add_handler(CommandHandler("whoami", whoami))

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook(PROJECT_URL + TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()
