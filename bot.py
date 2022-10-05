#!/usr/bin/env python


from curses import meta
import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean

engine = create_engine('sqlite:///Database/ALFA.db')
# Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)
# session = Session()

meta = MetaData()

taxiTable = Table(
    'taxi', meta,
    Column('id', Integer, primary_key=True),
    Column('from', String),
    Column('destination', String),
    Column('departure_time', String),
    Column('meetingPoint', String),
    Column('passenger1', String),
    Column('passenger2', String),
    Column('passenger3', String),
    Column('passenger4', String),
    Column('passenger5', String),
)

taxiUserData = {}



"""Simple inline keyboard bot with multiple CallbackQueryHandlers.

This Bot uses the Application class to handle the bot.
First, a few callback functions are defined as callback query handler. Then, those functions are
passed to the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot that uses inline keyboard that has multiple CallbackQueryHandlers arranged in a
ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line to stop the bot.
"""
import logging

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Stages
# START_ROUTES, END_ROUTES = range(2)
# Callback data
START_ROUTES, END_ROUTES,TYPING, TAXI,FLIGHT, FROM_ALFA,FROM_KIP,FROM_CRYSTAL, TO_ALFA, TO_KIP, DEPART_T, TO_CRYSTAL, COMPLETE_TAXI, THREE, FOUR, CREATE_RIDE, DEPART_TIME, MEETING_POINT, SELECTING_FEATURE, END = range(20)

CHOOSE_TAXI, SET_TIME, SET_MEETING_POINT  = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    keyboard = [
        [
            InlineKeyboardButton("Find people to share a cab", callback_data=str(TAXI)),
            # InlineKeyboardButton("Flight", callback_data=str(FLIGHT)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await update.message.reply_text("Can I help you with something?", reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return START_ROUTES


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=str(TAXI)),
            # InlineKeyboardButton("2", callback_data=str(FLIGHT)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.
    await query.edit_message_text(text="Start handler, Choose a route", reply_markup=reply_markup)
    return START_ROUTES


async def taxi_from(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("ALFA location", callback_data=str(FROM_ALFA))
        ],
        [
            InlineKeyboardButton("KIP Hotel", callback_data=str(FROM_KIP)),
            InlineKeyboardButton("Crystal Crown Hotel", callback_data=str(FROM_CRYSTAL))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Where are you at?", reply_markup=reply_markup
    )
    return START_ROUTES

async def taxi_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("KIP Hotel", callback_data=str(TO_KIP)),
            InlineKeyboardButton("Crystal Crown Hotel", callback_data=str(TO_CRYSTAL))
        ],
        [
            InlineKeyboardButton("ALFA event", callback_data=str(TO_ALFA))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    taxiUserData['from'] = query.data
    print(query.data)
    print('ok-----')
    print(update)
    print('ok-----')
    print(context)
    print('ok-----')
    print(taxiUserData)
    print('ok-----')

    await query.edit_message_text(
        text="Where do you go?", reply_markup=reply_markup
    )
    return START_ROUTES

async def existingTaxi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("12.15pm - 3 seats available", callback_data=str(FOUR)),
        ],
        [
            InlineKeyboardButton("12.30pm - 1 seat available", callback_data=str(FOUR))
        ],
        [
            InlineKeyboardButton("Create a new ride", callback_data=str(SELECTING_FEATURE))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    taxiUserData['to'] = query.data
    print(taxiUserData)
    print('ok++++')

    context.user_data['state'] = CHOOSE_TAXI

    # await update.callback_query.answer()
    await query.edit_message_text(
        text="Do you want to ride one of the following taxis?", reply_markup=reply_markup
    )
    return START_ROUTES


async def setDepartureTime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # user = update.message.from_user
    # logger.info("User %s did not send a location.", user.first_name)

    print (update)
    print (context)
    print ("-----------------")

    await update.message.reply_text(
        "What time do you want to meet others to take the taxi together?"
    )

    return DEPART_TIME

async def setMeetingPoint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    # logger.info("User %s did not send a location.", user.first_name)
    # await update.callback_query.answer()
    await update.message.reply_text(
       "Where is the meeting point?"
    )

    print('setMeetingPoint')
    print(taxiUserData)

    return TYPING

    # text = "Where is the metting point?"
    # # await update.callback_query.answer()
    # await update.callback_query.edit_message_text(text=text)

    # print(update.message)
    # print('ok000000')

    # return TYPING

async def ask_for_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Prompt user to input data for selected feature."""
    # context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = "Okay, tell me what time you want to meet for the taxi (e.g. 12.30pm)."

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return TYPING

async def save_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Save input for feature and return to feature selection."""

    # user_data[FEATURES][user_data[CURRENT_FEATURE]] = update.message.text

    # user_data[START_OVER] = True

    print(context.user_data['state'])
    print('-----')
    if context.user_data['state'] == CHOOSE_TAXI:
        context.user_data['state'] = SET_TIME
        taxiUserData['departure_time'] = update.message.text
        print("CHOOSE_TAXI")
        return await setMeetingPoint(update, context)
    elif context.user_data['state'] == SET_TIME:
        context.user_data['state'] = SET_MEETING_POINT
        taxiUserData['meetingPoint'] = update.message.text
        print("SET_MEETING_POINT")
        return await completeTaxi(update, context)
    else:
        return

    

async def completeTaxi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = 'Thanks, you just created a taxi \nfrom %s \nto %s \nmeeting at %s \nwhere: %s \n' % (taxiUserData['from'], taxiUserData['to'], taxiUserData['departure_time'], taxiUserData['meetingPoint'])
    # await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    # await update.message.reply_text(
    #    text
    # )

    await update.message.reply_text(
       'Thanks, you just created a taxi \nfrom: %s \nto: %s \nmeeting at: %s \nat: %s \n' % (taxiUserData['from'], taxiUserData['to'], taxiUserData['departure_time'], taxiUserData['meetingPoint'])
    )

    # query = update.callback_query
    # await query.answer()
    # keyboard = [
    #     [
    #         InlineKeyboardButton("Complete", callback_data=str(FROM_ALFA))
    #     ]
    # ]
    # reply_markup = InlineKeyboardMarkup(keyboard)
    # await query.edit_message_text(
    #     text="Finish taxi process", reply_markup=reply_markup
    # )
    return TYPING

async def flight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Enter a flight number", callback_data=str(THREE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="What's your flight number?", reply_markup=reply_markup
    )
    return START_ROUTES


async def three(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Yes, let's do it again!", callback_data=str(TAXI)),
            InlineKeyboardButton("Nah, I've had enough ...", callback_data=str(FLIGHT)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Third CallbackQueryHandler. Do want to start over?", reply_markup=reply_markup
    )
    # Transfer to conversation state `SECOND`
    return END_ROUTES


async def four(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            # InlineKeyboardButton("Flight", callback_data=str(FLIGHT)),
            # InlineKeyboardButton("3", callback_data=str(THREE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Fourth CallbackQueryHandler, Choose a route", reply_markup=reply_markup
    )
    return START_ROUTES


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    print('END')

    query = update.callback_query
    # await query.answer()
    await query.edit_message_text(text=f"Selected option: {query.data}")

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("5795299434:AAEk5XWtfc8Gj1rTtb6fCNS-3HjXjTYt8r8").build()

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(taxi_from, pattern="^" + str(TAXI) + "$"),
                CallbackQueryHandler(taxi_to, pattern="^" + str(FROM_ALFA) + "$"),
                CallbackQueryHandler(taxi_to, pattern="^" + str(FROM_KIP) + "$"),
                CallbackQueryHandler(taxi_to, pattern="^" + str(FROM_CRYSTAL) + "$"),
                CallbackQueryHandler(existingTaxi, pattern="^" + str(TO_ALFA) + "$"),
                CallbackQueryHandler(existingTaxi, pattern="^" + str(TO_KIP) + "$"),
                CallbackQueryHandler(existingTaxi, pattern="^" + str(TO_CRYSTAL) + "$"),
                CallbackQueryHandler(setDepartureTime, pattern="^" + str(DEPART_T) + "$"),
                # CallbackQueryHandler(setMeetingPoint, pattern="^" + str(MEETING_POINT) + "$"),
                CallbackQueryHandler(completeTaxi, pattern="^" + str(COMPLETE_TAXI) + "$"),
                CallbackQueryHandler(ask_for_input, pattern="^" + str(SELECTING_FEATURE) + "$"),
                # CallbackQueryHandler(createRide, pattern="^" + str(CREATE_RIDE) + "$"),
                CallbackQueryHandler(flight, pattern="^" + str(FLIGHT) + "$"),
                CallbackQueryHandler(three, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(four, pattern="^" + str(FOUR) + "$"),
            ],
            # SELECTING_FEATURE: [CallbackQueryHandler(ask_for_input, pattern="^(?!" + str(END) + ").*$")],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_input)],
            DEPART_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, setMeetingPoint)],
            MEETING_POINT: [MessageHandler(filters.TEXT & ~filters.COMMAND, completeTaxi)],
            END_ROUTES: [
                CallbackQueryHandler(start_over, pattern="^" + str(TAXI) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(FLIGHT) + "$"),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(completeTaxi, pattern="^" + str(MEETING_POINT) + "$"),
            CommandHandler("start", start),
        ],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
