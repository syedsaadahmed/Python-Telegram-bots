#!/usr/bin/python


from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging
import requests
import base64
import json

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

GENDER, PHOTO, LOCATION, BIO = range(4)


def start(bot, update):
    reply_keyboard = [['Boy', 'Girl', 'Other']]

    update.message.reply_text(
        'Hi! My name is Professor Bot. I will hold a conversation with you. '
        'and i will also tell you about yourself by seeing you'
        'Send /cancel to stop talking to me.\n\n'
        'Are you a boy or a girl?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return GENDER


def gender(bot, update):
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('I see! Please send me a photo of yourself, '
                              'so I know what you look like, or send /skip if you don\'t want to.',
                              reply_markup=ReplyKeyboardRemove())

    return PHOTO


def photo(bot, update):
    user = update.message.from_user
    photo_file = bot.get_file(update.message.photo[-1].file_id)
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')

    # put your keys in the header
    headers = {
        "Content-Type":"application/json",
        "app_id": "cd1c1528",
        "app_key": "5cc5ec30a6501f55923dcc7234c8fd04"
    }

    encoded_string = base64.b64encode(open("user_photo.jpg", 'r').read())
    payload_dict = {
        "image":encoded_string,
        "subject_id": "Picture",
        "gallery_name": "MyGallery"
    }
    payload = json.dumps(payload_dict)
    response = requests.post('https://api.kairos.com/detect', data=payload, headers=headers, verify=False)
    response_body = response.content

    data = json.loads(response_body)

    gender_info = 'Gender = ' + data['images'][0]['faces'][0]['attributes']['gender']['type']
    age = 'Age = ' + str(data['images'][0]['faces'][0]['attributes']['age'])
    lips = 'Lips are = ' + data['images'][0]['faces'][0]['attributes']['lips']
    glass = 'Glasses = ' + data['images'][0]['faces'][0]['attributes']['glasses']
    Confidence = 'Confidence = ' + str(data['images'][0]['faces'][0]['confidence'])
    Black = 'Black = ' + str(data['images'][0]['faces'][0]['attributes']['black'])
    Asian = 'Asian = ' + str(data['images'][0]['faces'][0]['attributes']['asian'])
    White = 'White = ' + str(data['images'][0]['faces'][0]['attributes']['white'])
    ########################API FOR EMOTIONS############################################
    subscription_key = "f1e6c6fe2a2641db912bcc921db98e84"

    #Key 2: c9fdee17bdd24741a5d4ee07bad9bc3e
    assert subscription_key
    headers_emo  = {'Ocp-Apim-Subscription-Key': subscription_key, "Content-Type": "application/octet-stream" }

    image_path = "user_photo.jpg"
    image_data = open(image_path, "rb").read()

    emotion_recognition_url = "https://westus.api.cognitive.microsoft.com/emotion/v1.0/recognize"

    response = requests.post(emotion_recognition_url, headers=headers_emo, data=image_data)
    analysis = response.content

    data2 = json.loads(analysis)

    sad = 'Saddness = ' + str(data2[0]['scores']['sadness'])
    happy = 'Happiness = ' + str(data2[0]['scores']['happiness'])
    surprise = 'Surprise = ' + str(data2[0]['scores']['surprise'])
    anger = 'Anger = ' + str(data2[0]['scores']['anger'])
    disgust = 'Disgust = ' + str(data2[0]['scores']['disgust'])
    fear = 'Fear = ' + str(data2[0]['scores']['fear'])
    neutral = 'Neutral = ' + str(data2[0]['scores']['neutral'])
    ##################################################################################

    #update.message.reply_text(data)
    update.message.reply_text('Gorgeous! Now, Here are some stats about you; \n {} \n {} \n {} \n {} \n {} \n {} \n {} \n {} \n {} \n {} \n {} \n {} \n {} \n {} \n {}'.format(gender_info,age,lips,glass,Confidence,Black,White,Asian,sad,happy,anger,fear,disgust,surprise,neutral))
    #return GENDER
    return ConversationHandler.END


def skip_photo(bot, update):
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text('No Problem, Good Bye, See you soon, /start to talk again')

    #return ConversationHandler.END
    return ConversationHandler.END

'''

def location(bot, update):
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)
    update.message.reply_text('Maybe I can visit you sometime! '
                              'Hope to see you Soon !.')

    return GENDER


def skip_location(bot, update):
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text('You seem a bit paranoid! '
                              'No Problem Buddy.')

    return GENDER



def bio(bot, update):
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END

'''
def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("471469781:AAEKDJZyw14MIKf2Gpd-Jj485XMXgJS1YDM")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            GENDER: [RegexHandler('^(Boy|Girl|Other)$', gender)],

            PHOTO: [MessageHandler(Filters.photo, photo),
                    CommandHandler('skip', skip_photo)],

            #LOCATION: [MessageHandler(Filters.location, location),
                       #CommandHandler('skip', skip_location)],

            #BIO: [MessageHandler(Filters.text, bio)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

