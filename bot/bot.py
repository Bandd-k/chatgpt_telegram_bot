import io
import logging
import asyncio
import traceback
import html
import json
from datetime import datetime, timedelta
import tempfile
from pathlib import Path
import pydub
import onboarding

import telegram
from telegram import (
    Update,
    User,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    WebAppInfo
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    AIORateLimiter,
    filters,
    ContextTypes
)
from telegram.constants import ParseMode, ChatAction

from mixpanel import Mixpanel
mp = Mixpanel("4acbbf84b424e3265bcc39e82cb3634b")

import config
import database
import openai_utils

from subgram import Subgram
from subgram.constants import EventType

subgram = Subgram(config.subgram_token)

MANAGE_SUBSCRIPTION_CALLBACK_DATA = "manage_subscription"
MANAGE_SUBSCRIPTION_MARKUP = InlineKeyboardMarkup([[
    InlineKeyboardButton("Управление подпиской", callback_data=MANAGE_SUBSCRIPTION_CALLBACK_DATA)
]])

# setup
db = database.Database()
logger = logging.getLogger(__name__)

user_semaphores = {}
user_tasks = {}

HELP_MESSAGE = """Команды:
⚪ /new – Начать новый диалог
⚪ /voice – Включить/выключить голосовые ответы
⚪ /topics – Выбрать тему для обсуждения
⚪ /dict слово – Показать словарь для слова
⚪ /stats - показывает вашу статистику
⚪ /help – Показать помощь

🎤 Попробуйте использовать <b>Голосовые сообщения</b> вместо текста
🤓 Не стесняйтесь задавать любые вопросы. Новые фразы, переводы слов, грамматические правила и т.д.
⏰ Говорите много. Ваша цель - отвечать очень подробно и использовать сложные предложения.
❤️ Попросите сменить тему, если хотите. Не бойтесь обидеть чувства бота.

Взаимодействуйте с AI English Tutor, как вы бы делали это с носителем языка. Бот исправит критические ошибки, и если вы что-то не понимаете, не стесняйтесь просить его перефразировать. Бот также может переводить, но оставьте это для критических ситуаций, когда понимание является существенным.
"""

reminder_tasks = {}
send_survey_tasks = {}
last_message_before_survey = {}

async def send_reminder(context: CallbackContext, user_id: int):
    reminder_time = 24 * 60 * 60  # 24 hours
    while True:
        await asyncio.sleep(reminder_time)
        chatgpt_instance = openai_utils.ChatGPT()
        dialog_messages = db.get_dialog_messages(user_id, dialog_id=None)
        _message = ""
        answer, _, _ = await chatgpt_instance.send_message(
            _message,
            dialog_messages=dialog_messages,
            chat_mode="reminder"
        )
        await context.bot.send_message(user_id, answer)
        new_dialog_message = {"user": "", "bot": answer, "date": datetime.now()}
        db.set_dialog_messages(
            user_id,
            dialog_messages + [new_dialog_message],
            dialog_id=None
        )

        survey_sent = db.get_user_attribute(user_id, "survey_sent")

        # if reminder is sent after unanswered survey (did not press buttons), 
        # set as if the survey was not sent. so that the survey will be resent.
        if survey_sent == 1:
            db.set_user_attribute(user_id, "survey_sent", 0)

        # if reminder is sent after unanswered survey (pressed button but did not type anything), 
        # set as if the user have completed the survey
        if survey_sent == 2:
            db.set_user_attribute(user_id, "survey_sent", 3)

        mp.track(user_id, 'send_reminder')


def split_text_into_chunks(text, chunk_size):
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]


async def register_user_if_not_exists(update: Update, context: CallbackContext, user: User):
    if not db.check_if_user_exists(user.id):
        db.add_new_user(
            user.id,
            update.message.chat_id,
            username=user.username,
            first_name=user.first_name,
            last_name= user.last_name
        )
        db.start_new_dialog(user.id)
        mp.track(user.id, 'register_user_if_not_exists -> adding a new user ')

    if db.get_user_attribute(user.id, "current_dialog_id") is None:
        db.start_new_dialog(user.id)

    if user.id not in user_semaphores:
        user_semaphores[user.id] = asyncio.Semaphore(1)

    # make sure all new variables available
    
    # tokens
        
    if db.get_user_attribute(user.id, "n_input_tokens") is None:
        db.set_user_attribute(user.id, "n_input_tokens", 0)
    if db.get_user_attribute(user.id, "n_output_tokens") is None:
        db.set_user_attribute(user.id, "n_output_tokens", 0)
    
    # voice enabled
    if db.get_user_attribute(user.id, "voice_mode") is None:
        db.set_user_attribute(user.id, "voice_mode", True)

    chat_mode = "general_english"
    if db.get_user_attribute(user.id, "current_chat_mode") is None:
        db.set_user_attribute(user.id, "current_chat_mode", chat_mode)


    # voice message transcription
    if db.get_user_attribute(user.id, "n_transcribed_seconds") is None:
        db.set_user_attribute(user.id, "n_transcribed_seconds", 0.0)

    # voice generated 
    if db.get_user_attribute(user.id, "n_voice_generated_characters") is None:
        db.set_user_attribute(user.id, "n_voice_generated_characters", 0)

    # words said
    if db.get_user_attribute(user.id, "n_words_said") is None:
        db.set_user_attribute(user.id, "n_words_said", 0)

    # max streak
    if db.get_user_attribute(user.id, "n_max_streak") is None:
        db.set_user_attribute(user.id, "n_max_streak", 1)

    # current streak start
    if db.get_user_attribute(user.id, "current_streak_start") is None:
        db.set_user_attribute(user.id, "current_streak_start", datetime.now())

async def voice_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.message.from_user)
    user_id = update.message.from_user.id

    db.set_user_attribute(user_id, "last_interaction", datetime.now())

    voice = not db.get_user_attribute(user_id, "voice_mode")
    db.set_user_attribute(user_id, "voice_mode", voice)

    answer = f"Голосовые сообщения от бота <b>" + ("включены" if voice else "выключены") + "</b>"

    await update.message.reply_text(answer, parse_mode=ParseMode.HTML)
    mp.track(user_id, 'voice_handle')

async def stats_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.message.from_user)
    user_id = update.message.from_user.id
    update_streak(user_id)
    db.set_user_attribute(user_id, "last_interaction", datetime.now())

    n_words_said = db.get_user_attribute(user_id, "n_words_said") or 0
    n_max_streak = db.get_user_attribute(user_id, "n_max_streak") or 0
    current_streak_start = db.get_user_attribute(user_id, "current_streak_start") or datetime.now()

    difference = datetime.now() - current_streak_start
    # Get the number of days from the difference
    number_of_days = difference.days + 1

    info_string = (
        f"📝 Word Count: <b>{n_words_said}</b>\n"
        f"🏆 Maximum Streak: <b>{n_max_streak}</b>\n"
        f"⏳ Current Streak: <b>{number_of_days}</b>"
    )

    await update.message.reply_text(info_string, parse_mode=ParseMode.HTML)
    mp.track(user_id, 'stats_handle')


async def dict_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.message.from_user)
    user_id = update.message.from_user.id

    db.set_user_attribute(user_id, "last_interaction", datetime.now())

    # Extract the first argument from the command
    try:
        input_parameter = context.args[0]
        # Perform your actions with input_parameter here
        response = await openai_utils.dictionary(input_parameter)
    except (IndexError, ValueError):
        response = 'Please provide an input parameter. Usage: /dict <input>'
    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    mp.track(user_id, 'dict_handle')


async def start_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.message.from_user)
    user_id = update.message.from_user.id

    db.set_user_attribute(user_id, "last_interaction", datetime.now())
    db.start_new_dialog(user_id)

    reply_text = "Hi! I'm <b>English Speaking trainer</b> 🤖\n\n"
    reply_text += HELP_MESSAGE

    await update.message.reply_text(reply_text, parse_mode=ParseMode.HTML)
    chat_mode = "general_english"
    db.set_user_attribute(user_id, "current_chat_mode", chat_mode)

    await update.message.reply_text(f"{config.chat_modes[chat_mode]['welcome_message']}", parse_mode=ParseMode.HTML)
    mp.track(user_id, 'start_handle')


async def help_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.message.from_user)
    user_id = update.message.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())
    await update.message.reply_text(HELP_MESSAGE, parse_mode=ParseMode.HTML)
    mp.track(user_id, 'help_handle')

def update_streak(user_id):
    n_max_streak = db.get_user_attribute(user_id, "n_max_streak")
    if n_max_streak is None:
        db.set_user_attribute(user_id, "n_max_streak", 1)

    current_streak_start = db.get_user_attribute(user_id, "current_streak_start")
    if current_streak_start is None:
        db.set_user_attribute(user_id, "current_streak_start", datetime.now())
        return

    n_max_streak = db.get_user_attribute(user_id, "n_max_streak")
    last_message_timestamp = db.get_user_attribute(user_id, "last_message_timestamp") or datetime.now()
    if datetime.now() - last_message_timestamp > timedelta(hours=24):
        # reset streak
        difference = last_message_timestamp - current_streak_start
        number_of_days = difference.days
        db.set_user_attribute(user_id, "n_max_streak", max(n_max_streak, number_of_days + 1))
        db.set_user_attribute(user_id, "current_streak_start", datetime.now())


async def message_handle(update: Update, context: CallbackContext, message=None, use_new_dialog_timeout=True, from_user = True):
    # check if message is edited
    if from_user and update.edited_message is not None:
        await edited_message_handle(update, context)
        return

    _message = message or update.message.text

    await register_user_if_not_exists(update, context, update.message.from_user)
    if await is_previous_message_not_answered_yet(update, context): return

    if from_user:
        user_id = update.message.from_user.id
    else:
        user_id = update.from_user.id

    if user_id in reminder_tasks:
        # cancel the old reminder task
        reminder_tasks[user_id].cancel()
    reminder_tasks[user_id] = asyncio.create_task(send_reminder(context, user_id))  # schedule a new reminder task

    if user_id in send_survey_tasks:
        # reset send survey timer
        send_survey_tasks[user_id].cancel()
    # if no survey was sent and the user is eligible
    survey_sent = db.get_user_attribute(user_id, "survey_sent") or 0
    total_words_said = db.get_user_attribute(user_id, "n_words_said") or 0
    messages_sent_total = db.get_user_attribute(user_id, "messages_sent_total") or 0
    if (survey_sent == 0) and (messages_sent_total > 10):
        # send survey in 15 minutes
        send_survey_tasks[user_id] = asyncio.create_task(send_survey_buttons(update))

    if survey_sent == 2: # user pressed survey button and bot is waiting for writted feedback
        await get_survey_text_answer(update)

    else: # handle regular messages                
        messages_sent_today = db.get_user_attribute(user_id, "messages_sent_today") or 0

        datetime_now = datetime.now()
        last_message_timestamp = db.get_user_attribute(user_id, "last_message_timestamp") or datetime.now()
        if (datetime_now.year, datetime_now.month, datetime_now.day) != (last_message_timestamp.year, last_message_timestamp.month, last_message_timestamp.day):
            messages_sent_today = 0

        # inline subgram.has_access() check to not make requests until the message quota is used
        if (messages_sent_total > 29 and messages_sent_today > 9) and not await subgram.has_access(
            user_id=update.effective_user.id,
            product_id=config.subgram_product_id,
        ):
            mp.track(user_id, 'no_subscription_block')
            await update.message.reply_text("К сожалению, у Вас закончились бесплатные сообщения с Чатти на сегодня. Возвращайтесь завтра или подключите подписку для безлимитный сообщений!")
            await manage_subscription(update, context)
        else:
            chat_mode = db.get_user_attribute(user_id, "current_chat_mode")

            async def message_handle_fn():
                # new dialog timeout
                if use_new_dialog_timeout:
                    if (datetime.now() - db.get_user_attribute(user_id, "last_interaction")).seconds > config.new_dialog_timeout and len(db.get_dialog_messages(user_id)) > 0:
                        db.start_new_dialog(user_id)
                        await update.message.reply_text(f"Starting new dialog due to timeout (<b>{config.chat_modes[chat_mode]['name']}</b> mode) ✅", parse_mode=ParseMode.HTML)
                
                #update statistics
                words_count = len(_message.split())
                db.set_user_attribute(user_id, "n_words_said", total_words_said + words_count)
                update_streak(user_id)

                db.set_user_attribute(user_id, "messages_sent_total", messages_sent_total + 1)
                db.set_user_attribute(user_id, "messages_sent_today", messages_sent_today + 1)
                db.set_user_attribute(user_id, "last_interaction", datetime_now)
                db.set_user_attribute(user_id, "last_message_timestamp", datetime_now)

                # in case of CancelledError
                n_input_tokens, n_output_tokens = 0, 0
                voice_mode = db.get_user_attribute(user_id, "voice_mode")

                try:
                    if _message is None or len(_message) == 0:
                        await update.message.reply_text("🥲 You sent <b>empty message</b>. Please, try again!", parse_mode=ParseMode.HTML)
                        return

                    dialog_messages = db.get_dialog_messages(user_id, dialog_id=None)

                    chatgpt_instance = openai_utils.ChatGPT()

                    # todo async
                    # send correction check response 
                    if len(dialog_messages):
                        await update.message.chat.send_action(action="typing")
                        last_message = dialog_messages[-1]
                        message_to_check_correction = f"""
                        Student: {last_message['user']}
                        Teacher: {last_message['bot']}
                        Student: {_message}
                        """

                        correction_answer, _, _ = await chatgpt_instance.send_message(
                            message_to_check_correction,
                            dialog_messages=[],
                            chat_mode="correction_check"
                        )
                        if correction_answer != "no_reply":
                            await update.message.reply_text(correction_answer[:4096])

                    answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed = await chatgpt_instance.send_message(
                        _message,
                        dialog_messages=dialog_messages,
                        chat_mode=chat_mode
                    )

                    # Chatty will reply to this message at the end of the survey to remind about the conversation 
                    last_message_to_reply_to_after_survey = update.message

                    if voice_mode:
                        # send audio answer  
                        with tempfile.TemporaryDirectory() as tmp_dir:
                            await update.message.chat.send_action(action="record_audio")
                            tmp_dir = Path(tmp_dir)
                            voice_mp3_path = tmp_dir / "voice.mp3"
                            voice_ogg_path = tmp_dir / "voice.ogg"
                            voice_part = answer.split("<b>")[0]
                            await openai_utils.generate_audio(voice_part, voice_mp3_path)
                            # Convert the MP3 file to OGG format.
                            # make async?
                            audio_segment = pydub.AudioSegment.from_mp3(voice_mp3_path)

                            audio_segment.export(voice_ogg_path, format="ogg", codec = "libopus")

                            # update n_voice_generated_characters
                            db.set_user_attribute(user_id, "n_voice_generated_characters", len(voice_part) + db.get_user_attribute(user_id, "n_voice_generated_characters"))
                            try:
                                last_message_to_reply_to_after_survey = await update.message.reply_voice(voice=open(voice_ogg_path, 'rb'))
                            except Exception as e:
                                if "Voice_messages_forbidden" in str(e):
                                    await update.message.reply_text("Вы заблокировали входящие аудиосообщения! Дайте разрешение на аудиосообщения или выключите их с помощью команды /voice")
                                else:
                                    raise

                        await update.message.chat.send_action(action="typing")
                        # send hidden transcription
                        await update.message.reply_text(f'<span class="tg-spoiler">{answer[:4096]}</span>', parse_mode=ParseMode.HTML)
                    
                    else:
                        await update.message.chat.send_action(action="typing")
                        last_message_to_reply_to_after_survey = await update.message.reply_text(answer[:4096])

                    # update user data
                    new_dialog_message = {"user": _message, "bot": answer, "date": datetime.now()}
                    db.set_dialog_messages(
                        user_id,
                        db.get_dialog_messages(user_id, dialog_id=None) + [new_dialog_message],
                        dialog_id=None
                    )

                    last_message_before_survey[user_id] = last_message_to_reply_to_after_survey.id

                    db.update_n_used_tokens(user_id, n_input_tokens, n_output_tokens)

                except asyncio.CancelledError:
                    # note: intermediate token updates only work when enable_message_streaming=True (config.yml)
                    db.update_n_used_tokens(user_id, n_input_tokens, n_output_tokens)
                    raise

                except Exception as e:
                    error_text = f"Something went wrong during completion. Reason: {e}"
                    logger.error(error_text)
                    mp.track(user_id, 'Error', {
                        "function": "message_handle_fn",
                        "error": error_text
                    })
                    await update.message.reply_text(error_text)
                    return

                # send message if some messages were removed from the context
                if n_first_dialog_messages_removed > 0:
                    if n_first_dialog_messages_removed == 1:
                        text = "✍️ <i>Note:</i> Your current dialog is too long, so your <b>first message</b> was removed from the context.\n Send /new command to start new dialog"
                    else:
                        text = f"✍️ <i>Note:</i> Your current dialog is too long, so <b>{n_first_dialog_messages_removed} first messages</b> were removed from the context.\n Send /new command to start new dialog"
                    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

            async with user_semaphores[user_id]:
                task = asyncio.create_task(message_handle_fn())
                user_tasks[user_id] = task

                try:
                    await task
                except asyncio.CancelledError:
                    await update.message.reply_text("✅ Canceled", parse_mode=ParseMode.HTML)
                else:
                    pass
                finally:
                    if user_id in user_tasks:
                        del user_tasks[user_id]

    mp.track(user_id, 'message_handle')

async def is_previous_message_not_answered_yet(update: Update, context: CallbackContext):

    await register_user_if_not_exists(update, context, update.message.from_user)

    user_id = update.message.from_user.id
    if user_semaphores[user_id].locked():
        text = "⏳ Please <b>wait</b> for a reply to the previous message\n"
        await update.message.reply_text(text, reply_to_message_id=update.message.id, parse_mode=ParseMode.HTML)
        return True
    else:
        return False


async def voice_message_handle(update: Update, context: CallbackContext):
    await update.message.chat.send_action(action="typing")

    await register_user_if_not_exists(update, context, update.message.from_user)
    if await is_previous_message_not_answered_yet(update, context): return

    user_id = update.message.from_user.id

    voice = update.message.voice
    voice_file = await context.bot.get_file(voice.file_id)
    
    # store file in memory, not on disk
    buf = io.BytesIO()
    await voice_file.download_to_memory(buf)
    buf.name = "voice.oga"  # file extension is required
    buf.seek(0)  # move cursor to the beginning of the buffer

    transcribed_text = await openai_utils.transcribe_audio(buf)
    text = f"🎤: <i>{transcribed_text}</i>"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    # update n_transcribed_seconds
    db.set_user_attribute(user_id, "n_transcribed_seconds", voice.duration + db.get_user_attribute(user_id, "n_transcribed_seconds"))

    await message_handle(update, context, message=transcribed_text)
    mp.track(user_id, 'voice_message_handle')

async def new_dialog_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.message.from_user)
    if await is_previous_message_not_answered_yet(update, context): return

    user_id = update.message.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())

    db.start_new_dialog(user_id)
    await update.message.reply_text("Starting new dialog ✅")

    chat_mode = db.get_user_attribute(user_id, "current_chat_mode")
    await update.message.reply_text(f"{config.chat_modes[chat_mode]['welcome_message']}", parse_mode=ParseMode.HTML)
    mp.track(user_id, 'new_dialog_handle')

def get_topics_menu(page_index: int):
    n_chat_modes_per_page = config.n_chat_modes_per_page
    topics = config.topics["topics"]
    text = f"Select <b>topics</b> ({len(topics)} topics available):"

    # buttons
    chat_mode_keys = topics
    page_chat_mode_keys = chat_mode_keys[page_index * n_chat_modes_per_page:(page_index + 1) * n_chat_modes_per_page]

    keyboard = []
    for chat_mode_key in page_chat_mode_keys:
        name = chat_mode_key
        keyboard.append([InlineKeyboardButton(name, callback_data=f"set_topics|{chat_mode_key}")])

    # pagination
    if len(chat_mode_keys) > n_chat_modes_per_page:
        is_first_page = (page_index == 0)
        is_last_page = ((page_index + 1) * n_chat_modes_per_page >= len(chat_mode_keys))

        if is_first_page:
            keyboard.append([
                InlineKeyboardButton("»", callback_data=f"show_topics|{page_index + 1}")
            ])
        elif is_last_page:
            keyboard.append([
                InlineKeyboardButton("«", callback_data=f"show_topics|{page_index - 1}"),
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("«", callback_data=f"show_topics|{page_index - 1}"),
                InlineKeyboardButton("»", callback_data=f"show_topics|{page_index + 1}")
            ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return text, reply_markup

async def show_topics_callback_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update.callback_query, context, update.callback_query.from_user)
    if await is_previous_message_not_answered_yet(update.callback_query, context): return

    user_id = update.callback_query.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())

    query = update.callback_query
    await query.answer()

    page_index = int(query.data.split("|")[1])
    if page_index < 0:
        return

    text, reply_markup = get_topics_menu(page_index)
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except telegram.error.BadRequest as e:
        mp.track(user_id, 'Error', {
            "function": "show_topics_callback_handle",
            "error": e
        })
        if str(e).startswith("Message is not modified"):
            pass
    mp.track(user_id, 'show_topics_callback_handle')

async def show_topics_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.message.from_user)
    if await is_previous_message_not_answered_yet(update, context): return

    user_id = update.message.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())

    text, reply_markup = get_topics_menu(0)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    mp.track(user_id, 'show_topics_handle')

async def send_survey_buttons(update: Update):
    await asyncio.sleep(15 * 60) # send after 15 minutes of no messages
    user_id = update.message.from_user.id
    db.set_user_attribute(user_id, "survey_sent", 1)

    text = "Спасибо, что общаетесь со мной! Насколько вероятно, что вы порекомендуете меня своим друзьям? Оцените, пожалуйста, от 0 до 10. Ваша оценка останется анонимной, но поможет моим разработчикам сделать меня еще лучше!"
    keyboard = [[InlineKeyboardButton(str(i), callback_data=f"survey_button_press|{i}")] for i in range(11)]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    mp.track(user_id, 'send_survey_buttons')

async def set_topics_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update.callback_query, context, update.callback_query.from_user)
    user_id = update.callback_query.from_user.id

    query = update.callback_query
    await query.answer()

    topic = query.data.split("|")[1]
    
    #do we need to reset dialog?
    db.start_new_dialog(user_id)
    message = f"let's discuss {topic}"
    await message_handle(update.callback_query, context, message=message, use_new_dialog_timeout=False, from_user=False)
    mp.track(user_id, 'set_topics_handle')

async def survey_button_press_handle(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id
    db.set_user_attribute(user_id, "survey_sent", 2)
    query = update.callback_query
    await query.answer()
    survey_answer = query.data.split("|")[1]

    mp.track(user_id, 'survey_value', {
        "survey_button": survey_answer
    })
    mp.people_set(user_id, {
        'survey_button': survey_answer, 
        'words_said_before_survey': db.get_user_attribute(user_id, "n_words_said"), 
    })
    db.set_user_attribute(user_id, "survey_button", survey_answer)

    await query.message.reply_text("Благодарю за оценку! Теперь, пожалуйста, напишите в одном сообщении, что, по вашему мнению, можно улучшить, чтобы я стала еще лучше. После отправки сообщения мы автоматически продолжим наш диалог и практику английского!", parse_mode=ParseMode.HTML)
    mp.track(user_id, 'survey_button_press_handle')

async def get_survey_text_answer(update: Update):
    user_id = update.message.from_user.id
    db.set_user_attribute(user_id, "survey_sent", 3)

    survey_text = update.message.text
    mp.track(user_id, 'survey_value', {
        "survey_text": survey_text
    })
    mp.people_set(user_id, {
        'survey_text': survey_text, 
    })
    db.set_user_attribute(user_id, "survey_text", survey_text)

    await update.message.reply_text("Отлично! Thank you so much! Теперь давайте продолжим наш разговор! 😊", reply_to_message_id=last_message_before_survey[user_id], parse_mode=ParseMode.HTML) 
    mp.track(user_id, 'get_survey_text_answer')

def total_spending(user_id):
    total_n_spent_dollars = 0
    total_n_used_tokens = 0

    n_input_tokens = db.get_user_attribute(user_id, "n_input_tokens") or 0
    n_output_tokens = db.get_user_attribute(user_id, "n_output_tokens") or 0
    n_transcribed_seconds = db.get_user_attribute(user_id, "n_transcribed_seconds") or 0
    n_voice_generated_characters = db.get_user_attribute(user_id, "n_voice_generated_characters") or 0

    details_text = "🏷️ Details:\n"
    model_key = config.models["current_model"]

    # tokens 
    total_n_used_tokens += n_input_tokens + n_output_tokens

    n_input_spent_dollars = config.models["info"][model_key]["price_per_1000_input_tokens"] * (n_input_tokens / 1000)
    n_output_spent_dollars = config.models["info"][model_key]["price_per_1000_output_tokens"] * (n_output_tokens / 1000)
    total_n_spent_dollars += n_input_spent_dollars + n_output_spent_dollars

    details_text += f"- {model_key}: <b>{n_input_spent_dollars + n_output_spent_dollars:.03f}$</b> / <b>{n_input_tokens + n_output_tokens} tokens</b>\n"

    # voice recognition
    voice_recognition_n_spent_dollars = config.models["info"]["whisper"]["price_per_1_min"] * (n_transcribed_seconds / 60)
    if n_transcribed_seconds != 0:
        details_text += f"- Whisper (voice recognition): <b>{voice_recognition_n_spent_dollars:.03f}$</b> / <b>{n_transcribed_seconds:.01f} seconds</b>\n"

    total_n_spent_dollars += voice_recognition_n_spent_dollars

    # voice generation

    voice_generation_n_spent_dollars = config.models["info"]["voice_generation"]["price_per_1000_characters"] * (n_voice_generated_characters / 1000)
    if n_transcribed_seconds != 0:
        details_text += f"- Voice generation: <b>{voice_generation_n_spent_dollars:.03f}$</b> / <b>{n_voice_generated_characters} characters</b>\n"

    total_n_spent_dollars += voice_generation_n_spent_dollars

    text = f"You spent <b>{total_n_spent_dollars:.03f}$</b>\n"
    text += f"You used <b>{total_n_used_tokens}</b> tokens\n\n"
    text += details_text
    return total_n_spent_dollars

async def show_all_spending_handle(update: Update, context: CallbackContext):
    text = ""
    users = db.get_all_user_ids()
    for id in users:
        username = db.get_user_attribute(id, "username")
        text += f"{username} spent {total_spending(id)}\n"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def edited_message_handle(update: Update, context: CallbackContext):
    if update.edited_message.chat.type == "private":
        text = "🥲 Unfortunately, message <b>editing</b> is not supported"
        await update.edited_message.reply_text(text, parse_mode=ParseMode.HTML)

async def handle_subgram_events(bot):
    async for event in subgram.event_listener():
        try: 
            if event.type == EventType.SUBSCRIPTION_STARTED:
                mp.track(event.object.customer.telegram_id, 'SUBSCRIPTION_STARTED')
                await bot.send_message(
                    chat_id=event.object.customer.telegram_id,
                    text="✅ Безлимитная подписка активирована!"
                )

            if event.type == EventType.SUBSCRIPTION_CANCELLED:
                mp.track(event.object.customer.telegram_id, 'SUBSCRIPTION_CANCELLED')
                await bot.send_message(
                    chat_id=event.object.customer.telegram_id,
                    text=f"Вы успешно отписались! У Вас остается подписка до: {event.object.status.ending_at}."
                )

            if event.type == EventType.SUBSCRIPTION_UPGRADED:
                mp.track(event.object.customer.telegram_id, 'SUBSCRIPTION_UPGRADED')
                await bot.send_message(
                    chat_id=event.object.customer.telegram_id,
                    text=f"Вы улучшили Вашу подписку и Ваша подписка до: {event.object.status.ending_at}."
                )

            if event.type == EventType.SUBSCRIPTION_RENEW_FAILED:
                mp.track(event.object.customer.telegram_id, 'SUBSCRIPTION_RENEW_FAILED')
                await bot.send_message(
                    chat_id=event.object.customer.telegram_id,
                    text=f"У нас не получилось обновить Вашу подписку. Пожалуйста, проверьте способ оплаты.\nВаша подписка до: {event.object.status.ending_at}",
                    reply_markup=MANAGE_SUBSCRIPTION_MARKUP,
                )
        except Exception as e:
            error_text = f"Something went wrong during handle_subgram. Reason: {e}"
            logger.error(error_text)
            mp.track(event.object.customer.telegram_id, 'Error', {
                "function": "handle_subgram_events",
                "error": error_text
            })

async def manage_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    checkout_page = await subgram.create_checkout_page(
        product_id=config.subgram_product_id,
        user_id=update.effective_user.id,
        name=update.effective_user.name,
        language_code=update.effective_user.language_code,
    )

    return await update.effective_user.send_message(
        "⬇️ Управление подпиской ⬇️",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Chatty Unlimited", web_app=WebAppInfo(url=checkout_page.checkout_url))
        ]]),
    )

async def error_handle(update: Update, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    mp.track(update.effective_chat.id, 'Error', {
        "function": "error_handle",
        "error": str(context.error)
    })

    try:
        # collect error message
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            f"An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )

        # split text into multiple messages due to 4096 character limit
        for message_chunk in split_text_into_chunks(message, 4096):
            try:
                await context.bot.send_message(update.effective_chat.id, message_chunk, parse_mode=ParseMode.HTML)
            except telegram.error.BadRequest:
                # answer has invalid characters, so we send it without parse_mode
                await context.bot.send_message(update.effective_chat.id, message_chunk)
    except:
        await context.bot.send_message(update.effective_chat.id, "Some error in error handler")

async def post_init(application: Application):
    asyncio.create_task(handle_subgram_events(application.bot))
    await application.bot.set_my_commands([
        BotCommand("/new", "Начать новый диалог"),
        BotCommand("/voice", "Включить/выключить голосовые сообщения"),
        BotCommand("/topics", "Выбрать темы для разговоров"),
        # Clicking /dict doesn't work without a word
        # BotCommand("/dict", "Show dictionary for the word"),
        BotCommand("/stats", "Показать статистику использования"),
        BotCommand("/help", "Как пользоваться ботом"),
        BotCommand("/unlimited", "Управление безлимитной подпиской"),
    ])

def run_bot() -> None:
    application = (
        ApplicationBuilder()
        .token(config.telegram_token)
        .concurrent_updates(True)
        .rate_limiter(AIORateLimiter(max_retries=5))
        .http_version("1.1")
        .get_updates_http_version("1.1")
        .post_init(post_init)
        .build()
    )

    # add handlers
    user_filter = filters.ALL
    if len(config.allowed_telegram_usernames) > 0:
        usernames = [x for x in config.allowed_telegram_usernames if isinstance(x, str)]
        any_ids = [x for x in config.allowed_telegram_usernames if isinstance(x, int)]
        user_ids = [x for x in any_ids if x > 0]
        group_ids = [x for x in any_ids if x < 0]
        user_filter = filters.User(username=usernames) | filters.User(user_id=user_ids) | filters.Chat(chat_id=group_ids)

    admin_filter = filters.User(username=["karpenoid"])

    application.add_handler(onboarding.conversation_handler) #filters?

    application.add_handler(CommandHandler("help", help_handle, filters=user_filter))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & user_filter, message_handle))
    application.add_handler(CommandHandler("new", new_dialog_handle, filters=user_filter))

    application.add_handler(MessageHandler(filters.VOICE & user_filter, voice_message_handle))

    application.add_handler(CommandHandler("voice", voice_handle, filters=user_filter))
    application.add_handler(CommandHandler("dict", dict_handle, filters=user_filter, has_args=True))

    application.add_handler(CommandHandler("topics", show_topics_handle, filters=user_filter))
    application.add_handler(CallbackQueryHandler(show_topics_callback_handle, pattern="^show_topics"))
    application.add_handler(CallbackQueryHandler(set_topics_handle, pattern="^set_topics"))
    application.add_handler(CallbackQueryHandler(survey_button_press_handle, pattern="^survey_button_press"))

    application.add_handler(CommandHandler("stats", stats_handle, filters=user_filter))

    application.add_handler(CommandHandler("unlimited", manage_subscription, filters=user_filter))
    application.add_handler(CallbackQueryHandler(manage_subscription, MANAGE_SUBSCRIPTION_CALLBACK_DATA))

    # admin commands
    application.add_handler(CommandHandler("spending", show_all_spending_handle, filters=admin_filter))

    application.add_error_handler(error_handle)

    # start the bot
    application.run_polling()


if __name__ == "__main__":
    run_bot()

