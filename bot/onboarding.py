from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import asyncio

logger = logging.getLogger(__name__)
from mixpanel import Mixpanel
mp = Mixpanel("4acbbf84b424e3265bcc39e82cb3634b")

STEPS = [
    {
        "text": ["Привет, я Chatty - бот для болтания на английском!"],
        "button": "Привет",
    },
    {
        "text": [
            "Всем кто изучает язык не хватает языковой практики. Я помогу это исправить! Можешь говорить со мной когда захочешь и на любую тему.",
            "Не бойся допускать ошибки, долго думать или сбиваться с темы. Говори на любую интересную тебе тему, переспрашивай, проси повторить!",
            "У меня много свободного времени 😊"
        ],
        "button": "Круто",
    },
    {
        "text": [
            "Старайся записывать голосовые сообщения для практики речи.",
            "Строй более сложные предложения, используй новые слова, не отвечай короткими фразами. Следи за своим произношением.",
            "Итоговый результат зависит только от тебя!"
        ],
        "button": "Буду стараться!",
    },
    {
        "text": [
            "У бота есть несколько опциональных команд:",
            "/new - начать новый разговор.\n/topics - выбрать какую-то тему.\n/dict Слово - Спросить определение слова.\n/stats - Узнать твою статистику использования",
            "Хочешь новую тему - так и скажи: \"Let's talk about travelling to London\"",
            "Не знаешь слово? Скажи: \"Explain the word Itinerary\""
        ],
        "button": "Супер!",
    },
    {
        "text": [
            "Со следующего шага я перейду на английский и больше не буду использовать русский язык:)",
            "Первое время тебе будет тяжело, но это обязательный этап обучения, со временем общаться станет легко! Главное не забрасывай наши разговоры.",
            "Дети учат язык не зная ни одного слова и у них нет возможности спросить перевода 🙂"
        ],
        "button": "Let's start!",
    },
    {
        "text": ["Now let's finally chat in English! Please tell me about yourself! What is your name? Where are you from?"],
    }
]

async def handler(update, context, step_index):
    step = STEPS[step_index]
    query = update
    if step_index == 0:
        tracking_id = 0
        if context.args and len(context.args):
            tracking_id = context.args[0]
        mp.track(update.message.from_user.id, 'onboarding', {
            "step": str(step_index),
            "tracking_id": tracking_id
        })
        mp.people_set(update.message.from_user.id, {
            "tracking_id": tracking_id
        })
    else:
        query = update.callback_query
        await query.answer()
        mp.track(update.callback_query.from_user.id, 'onboarding', {
            "step": str(step_index),
        })

    for text in step["text"]:
        if text == step["text"][-1] and "button" in step:
            keyboard = [[InlineKeyboardButton(step["button"], callback_data=str(step_index + 1))]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(text, reply_markup=reply_markup)
        else:
            await query.message.reply_text(text)
            await asyncio.sleep(2)

    return step_index + 1 if step_index + 1 < len(STEPS) else ConversationHandler.END

conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', lambda u, c: handler(u, c, 0))],
    states={i: [CallbackQueryHandler(lambda u, c, i=i: handler(u, c, i), pattern=f'^{i}$')] for i in range(1, len(STEPS))},
    fallbacks=[CommandHandler('start', lambda u, c: handler(u, c, 0))],
)
