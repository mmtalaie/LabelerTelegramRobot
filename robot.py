from __future__ import unicode_literals
import os
# import unicodecsv as csv
import csv
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, message, user
import shutil
# pip install pytest-shutil
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Stages
SELECT_LABELING, SENTENCE_LABELING, WORD_LABELING = range(3)

WORD = 'word'
SENTENCE = 'Sentenc'

# lable data
WHITE, YELLOW, ORANGE, RED, END = range(5)

headerCsvFile = ['word', 'lable']


def start(update: Update, context: CallbackContext) -> int:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    global user
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    keyboard = [
        [
            InlineKeyboardButton("تشخیص کلمات نامناسب", callback_data=WORD),
            # InlineKeyboardButton("برچسب زدن جمله", callback_data=SENTENCE),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    update.message.reply_text(
        "سلام لطفا موضوع برچسب را انتخاب کنید", reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return SELECT_LABELING


def lableWord(update: Update, context: CallbackContext) -> int:
    global writer
    global csvFile
    # user = update.message.from_user
    if(not os.path.exists("Data/{}.txt".format(user.id))):
        shutil.copy("Data/Words.txt", "Data/{}.txt".format(user.id))

    newWordPolling(update, context)
    return WORD_LABELING


def openCsvWriter():
    if(not os.path.exists("Label/{}.txt".format(user.id))):
        csvFile = open("Label/{}.txt".format(user.id),
                       'a', encoding='utf-8', newline='')
        writer = csv.DictWriter(csvFile, dialect=csv.excel,
                                fieldnames=headerCsvFile)
        writer.writeheader()
    else:
        csvFile = open("Label/{}.txt".format(user.id),
                       'a', encoding='utf-8', newline='')
        writer = csv.DictWriter(csvFile, dialect=csv.excel,
                                fieldnames=headerCsvFile)

    return writer


def getLastWord():
    f = open("Data/{}.txt".format(user.id), "r+")
    d = f.readlines()
    lastWord = d[0]
    f.close()
    return lastWord


def removeLastWord():
    f = open("Data/{}.txt".format(user.id), "r+")
    d = f.readlines()
    f.seek(0)
    d.pop(0)
    for line in d:
        f.write(line)
    f.truncate()
    f.close()


def newWordPolling(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("سفید", callback_data=str(WHITE)),
            InlineKeyboardButton("زرد", callback_data=str(YELLOW)),
            InlineKeyboardButton("نارنجی", callback_data=str(ORANGE)),
            InlineKeyboardButton("قرمز", callback_data=str(RED)),
            InlineKeyboardButton("پایان", callback_data=str(END)),
            # InlineKeyboardButton("برچسب زدن جمله", callback_data=SENTENCE),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    lastWord = getLastWord()
    # Send message with text and appended InlineKeyboard
    textMessage = "برچسب کلمه را وارد کنید. کلمه \n کلمه: {}".format(
        lastWord)
    print(textMessage)
    query = update.callback_query
    query.answer()
    query.edit_message_text(textMessage, reply_markup=reply_markup)

    # csvFile.close()


# csvFile = open("Label/label.txt", 'a', encoding='utf-8', newline='')
# reader = csv.reader(csvFile)
    # row = {'word': lastLine.strip(), 'lable': '1'}
    # writer.writerow(row)
# for row in reader:
#     row.

def white(update: Update, context: CallbackContext):
    writer = openCsvWriter()
    lasetWord = getLastWord()
    row = {'word': lasetWord.strip(), 'lable': WHITE}
    removeLastWord()
    writer.writerow(row)
    newWordPolling(update, context)
    return WORD_LABELING


def yellow(update: Update, context: CallbackContext):
    writer = openCsvWriter()
    lasetWord = getLastWord()
    row = {'word': lasetWord.strip(), 'lable': YELLOW}
    removeLastWord()
    writer.writerow(row)
    newWordPolling(update, context)
    return WORD_LABELING


def orange(update: Update, context: CallbackContext):
    writer = openCsvWriter()
    lasetWord = getLastWord()
    row = {'word': lasetWord.strip(), 'lable': ORANGE}
    removeLastWord()
    writer.writerow(row)
    newWordPolling(update, context)
    return WORD_LABELING


def red(update: Update, context: CallbackContext):
    writer = openCsvWriter()
    lasetWord = getLastWord()
    row = {'word': lasetWord.strip(), 'lable': RED}
    removeLastWord()
    writer.writerow(row)
    newWordPolling(update, context)
    return WORD_LABELING


def end(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="ممنون از همکاری شما")
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("Token")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_LABELING: [
                CallbackQueryHandler(lableWord, pattern='^' + str(WORD) + '$'),
            ],
            SENTENCE_LABELING: [
                # CallbackQueryHandler(start_over, pattern='^' + str(ONE) + '$'),

                # CallbackQueryHandler(end, pattern='^' + str(TWO) + '$')
            ],
            WORD_LABELING:
            [
                CallbackQueryHandler(white, pattern='^' + str(WHITE) + '$'),
                CallbackQueryHandler(yellow, pattern='^' + str(YELLOW) + '$'),
                CallbackQueryHandler(orange, pattern='^' + str(ORANGE) + '$'),
                CallbackQueryHandler(red, pattern='^' + str(RED) + '$'),
                CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
            ]
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # Add ConversationHandler to dispatcher that will be used for handling updates
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
