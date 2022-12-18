import logging
import traceback
import html
import json
import pickle
from telegram import __version__ as TG_VER
import os
PORT = int(os.environ.get('PORT', 5000))
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
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


logger = logging.getLogger(__name__)
accessUserId = [912008246, 1730680339]
forwardChannelIds = []
# forwardChannelIds = [-1001808402675, -1001643352266]



def insert_data_into_pickle(opData):
    data = []
    data.append(opData)
    # open a file, where you ant to store the data
    file = open('openpositions', 'wb')
    # dump information to that file
    pickle.dump(data, file)
    # close the file
    file.close()


def read_data_pickle():
    import pickle
    # open a file, where you stored the pickled data
    file = open('openpositions', 'rb')
    # dump information to that file
    data = pickle.load(file)
    # close the file
    file.close()
    return data[0]


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id in accessUserId:
        await update.message.reply_html(
            rf"""
Hi {user.mention_html()}, Thanks for reaching out.
Here are my commands.
            
/aboutme -> Info on who I am
/openpositions -> See all open LATAM contracts
/contactinfo -> My contact info and LinkedIn
/resumeservice -> More info about my resume creation
/addopenpositions -> Add open positions
/set -> starting up auto forward message timer
/adduser -> add admin users
/addchannel -> add channels id to auto forward group
    """
        )
    else:
        await update.message.reply_html(
            rf"""
Hi {user.mention_html()}, Thanks for reaching out.
Here are my commands.
            
/aboutme -> Info on who I am
/openpositions -> See all open LATAM contracts
/contactinfo -> My contact info and LinkedIn
/resumeservice -> More info about my resume creation"""
        )



async def aboutme_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("""My name is Robert Grootjen and I'm a technical headhunter focused on seeking the best tech talent in Latin America. My main mission is to be the most reliable bridge between North America and LATAM.""")


async def contactinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("""Email: robert@latamrecruit.com
Linkedin: https://www.linkedin.com/in/robert-grootjen-08a10b15a/""")


async def openpositions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    currentOpenPositions = read_data_pickle()
    await update.message.reply_text(currentOpenPositions)


async def resumeservice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("""I will rebuild your resume to a very simple, consice and precise PDF file, readable for every recruiter and company.

Did you know recruiters sometimes discard candidates if they're not able to read the resume clearly?

It costs $20 USD and I will create it in English.

If you're interested, please send me your resume and pay here:
grootjentech.gumroad.com/l/resumeservice """)


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    currentOpenPositions = read_data_pickle()
    for i in forwardChannelIds:
        await context.bot.send_message(i, text=currentOpenPositions)


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    if chat_id in accessUserId:
        try:
            # args[0] should contain the time for the timer in seconds
            job_removed = remove_job_if_exists(str(chat_id), context)
            # context.job_queue.run_daily(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)
            context.job_queue.run_repeating(alarm, interval=86400, first=10, data=str(chat_id), chat_id=chat_id)

            text = "Timer successfully set!"
            if job_removed:
                text += " Old one was removed."
            await update.effective_message.reply_text(text)

        except (IndexError, ValueError):
            await update.effective_message.reply_text("Usage: /set <seconds>")
    else:
        await update.effective_message.reply_text("You are not authorized to access ")


async def add_openpositions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    currentOpenpositions = update.message.text
    print(currentOpenpositions)
    currentOpenpositions = currentOpenpositions.replace('/addopenpositions', '')
    currentOpenpositions = currentOpenpositions.lstrip()
    
    chat_id = update.effective_message.chat_id
    if chat_id in accessUserId:
        insert_data_into_pickle(currentOpenpositions)
        await update.message.reply_text("Open positions updated successfully")
    else:
        await update.effective_message.reply_text("You are not authorized to access ")

async def add_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    if chat_id in accessUserId:
        accessUserId.append((int(context.args[0])))
        await update.message.reply_text("User has added successfully!")
    else:
        await update.effective_message.reply_text("You are not authorized to access ")


async def add_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    if chat_id in accessUserId:
        forwardChannelIds.append((int(context.args[0])))
        await update.message.reply_text("Channel has added successfully!")
    else:
        await update.effective_message.reply_text("You are not authorized to access ")

DEVELOPER_CHAT_ID = "912008246"


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )



async def bad_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Raise an error to trigger the error handler."""
    await context.bot.wrong_method_name()  # type: ignore[attr-defined]


def main() -> None:
    application = Application.builder().token("5860704176:AAHYGwwnky3kPmsYW44TpHleMv6BqbDRN3U").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("aboutme", aboutme_command))
    application.add_handler(CommandHandler("contactinfo", contactinfo_command))
    application.add_handler(CommandHandler("openpositions", openpositions_command))
    application.add_handler(CommandHandler("addopenpositions", add_openpositions_command))
    application.add_handler(CommandHandler("resumeservice", resumeservice_command))
    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("adduser", add_user_command))
    application.add_handler(CommandHandler("addchannel", add_channel_command))
    application.add_handler(CommandHandler("bad_command", bad_command))
    # ...and the error handler
    application.add_error_handler(error_handler)
    application.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path="5860704176:AAHYGwwnky3kPmsYW44TpHleMv6BqbDRN3U",
    webhook_url="https://mighty-everglades-75025.herokuapp.com/" + "5860704176:AAHYGwwnky3kPmsYW44TpHleMv6BqbDRN3U")

    application.bot.setWebhook("https://mighty-everglades-75025.herokuapp.com/" + "5860704176:AAHYGwwnky3kPmsYW44TpHleMv6BqbDRN3U")
    # application.run_polling()


if __name__ == "__main__":
    main()