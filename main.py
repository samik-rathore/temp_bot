import logging
import python_weather
import datetime
from telegram import __version__ as TG_VER
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text("Hi!\nUse /get_temp to start getting notified of temperature at New Delhi every hour \nUse /stop to stop getting notifications")


async def temp(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    async with python_weather.Client(format=python_weather.METRIC) as client:

            # fetching the weather forecast
            weather = await client.get("New Delhi")
        
            # returns the current day's forecast temperature (in celsius)
            temp = weather.current.temperature
    await context.bot.send_message(
        job.chat_id, text=f"Hey! the current temperature at New Delhi is {temp} degree celsius!"
    )


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""

    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def get_temp(update: Update, context) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id

    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_repeating(
        temp, datetime.timedelta(hours = 1),first=1,chat_id=chat_id, name=str(chat_id), data=None
    )

    text = "You will get temperature notifications of New Delhi every hour"
    if job_removed:
        text += " Old one was removed."
    await update.effective_message.reply_text(text)




async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user wants to stop getting notifications"""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = (
        "successfully stopped!" if job_removed else "You have no active temperature notifier"
    )
    await update.message.reply_text(text)


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token("*****TOKEN*****")
        .build()
    )
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("get_temp", get_temp))
    application.add_handler(CommandHandler("stop", stop))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
