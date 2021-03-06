#%%
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to send timed Telegram messages.
This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from pathlib import Path
import datetime
from dateutil import tz
import message_strings
import util

from telegram.ext import Updater, CommandHandler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    update.message.reply_text(message_strings.USAGE_STRING)


def alarm(context):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(
        job.context, text="Pipi Tanz, Pipi Tanz, Zeit für Pipi Tanz!"
    )


def set_timer(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time
        time_string = context.args[util.CONTEXT_ARGS_TIME_INDEX]
        hour_string, minute_string = time_string.split(":")
        hour = int(hour_string)
        minute = int(minute_string)

        # Get timezone or use local if none is set
        # TODO Add timezone feature
        # timezone = util.getitem(context.args, util.CONTEXT_ARGS_TIMEZONE_INDEX, tz.tzlocal())

        reminder_time = datetime.time(hour, minute, tzinfo=tz.tzlocal())

        # Add job to queue and stop current one if there is a timer already
        new_job = context.job_queue.run_daily(alarm, reminder_time, context=chat_id)
        if not "jobs" in context.chat_data:
            # Initialize list of jobs
            context.chat_data["jobs"] = []

        # Add new job to list of Jobs
        context.chat_data["jobs"] = context.chat_data["jobs"] + [new_job]

        # Calculate when the next alarm is due
        now = datetime.datetime.now()
        next_alarm = now.replace(hour=reminder_time.hour, minute=reminder_time.minute)
        if next_alarm < now:
            # Alarm due tomorrow, adapt next_alarm accordingly
            one_day_delta = datetime.timedelta(days=+1)
            next_alarm = next_alarm + one_day_delta

        alarm_due_delta = next_alarm - now

        update.message.reply_text(message_strings.SUCCESS.format(alarm_due_delta))
        update.message.reply_text(
            f"You currently have {len(context.chat_data['jobs'])} reminders"
        )

    except (IndexError, ValueError):
        update.message.reply_text(message_strings.USAGE_STRING)


def unset(update, context):
    """Remove the job if the user changed their mind."""
    if "jobs" not in context.chat_data:
        update.message.reply_text("You have no active reminders")
        return

    for i, job in enumerate(context.chat_data["jobs"]):
        job.schedule_removal()
    del context.chat_data["jobs"]

    update.message.reply_text(f"{i+1} reminders successfully removed!")


def main():
    """Run bot."""

    # Load secret
    with open(Path("./token.secret")) as file:
        token = file.readline()

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token=token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(
        CommandHandler(
            "set", set_timer, pass_args=True, pass_job_queue=True, pass_chat_data=True
        )
    )
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


#%%

if __name__ == "__main__":
    main()
