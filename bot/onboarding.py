from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging

logger = logging.getLogger(__name__)
from mixpanel import Mixpanel
mp = Mixpanel("4acbbf84b424e3265bcc39e82cb3634b")

STEPS = [
    {
        "text": ["Привет, я бот для болтания на английском."],
        "button": "Привет",
    },
    {
        "text": [
            "Всем кто изучает язык не хватает языковой практики. Я буду это исправлять. Можешь говорить со мной когда захочешь и на любую тему.",
            "Не бойся допускать ошибки, мычать, сбиваться с темы. Спрашивай абсолютно любой вопрос, переспрашивай, проси повторить!",
            "У меня куча свободного времени 🙂"
        ],
        "button": "Круто",
    },
    {
        "text": [
            "Старайся использовать только голосовые сообщения.",
            "Строй более сложные предложения, используй новые слова, не отвечай короткими фразами. Следи за своим произношением.",
            "Итоговый результат зависит только от тебя самого!"
        ],
        "button": "Буду стараться!",
    },
    {
        "text": [
            "Несколько вспомогательных команд. Но их лучше не использовать.",
            "/new - начать новый разговор.\n/topics - выбрать какую-то тему.\n/dict Слово - Спросить определение слова.",
            "Поясню",
            "Хочешь новую тему - так и скажи Let's talk about the idea of an infinite universe",
            "Не знаешь слово? Скажи I don't know the word 'infinite', could you explain it to me?"
        ],
        "button": "Все уже ясно, может начнем",
    },
    {
        "text": [
            "Со следующего шага я перейду на английский и больше не буду использовать русский язык:)",
            "Первое время тебе будет тяжело, но это обязательный этап обучения, со временем общаться станет легко! Главное не забрасывай наши разговоры.",
            "Дети учат язык не зная ни одного слова и у них нет возможности спросить перевода 🙂"
        ],
        "button": "LETSGOOO",
    },
    {
        "text": ["Hey! My Russian alter ego has explained you the basics. Now let's talk. Tell me about yourself?"],
    }
]

async def handler(update, context, step_index):
    step = STEPS[step_index]
    query = update
    if step_index > 0 :
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

    return step_index + 1 if step_index + 1 < len(STEPS) else ConversationHandler.END

conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', lambda u, c: handler(u, c, 0))],
    states={i: [CallbackQueryHandler(lambda u, c, i=i: handler(u, c, i), pattern=f'^{i}$')] for i in range(1, len(STEPS))},
    fallbacks=[CommandHandler('start', lambda u, c: handler(u, c, 0))],
)
