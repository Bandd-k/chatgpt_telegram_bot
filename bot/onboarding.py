from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Defining states
GREET, COOL, TRYING, UNDERSTOOD, READY, LETSGO = range(6)

# Start command handler
def start(update, context):
    keyboard = [[InlineKeyboardButton("Привет", callback_data='greet')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Привет, я бот для болтания на английском.', reply_markup=reply_markup)
    return GREET

# Greet handler
def greet(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Всем кто изучает язык не хватает языковой практики. Я буду это исправлять. Можешь говорить со мной когда захочешь и на любую тему.")
    query.message.reply_text("Не бойся допускать ошибки, мычать, сбиваться с темы. Спрашивай абсолютно любой вопрос, переспрашивай, проси повторить! У меня куча свободного времени 🙂")
    keyboard = [[InlineKeyboardButton("Круто", callback_data='cool')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(reply_markup=reply_markup)
    return COOL

# Cool handler
def cool(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Стара́йся использовать только голосовые сообщения.")
    query.message.reply_text("Строй более сложные предложения, используй новые слова, не отвечай короткими фразами. Следи за своим произношением.")
    query.message.reply_text("Итоговый результат зависит только от тебя самого!")
    keyboard = [[InlineKeyboardButton("Буду стараться!", callback_data='trying')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(reply_markup=reply_markup)
    return TRYING

# Trying handler
def trying(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="У меня есть только одна команда")
    query.message.reply_text("/voice - включить выключить голосовые сообщения.")
    keyboard = [[InlineKeyboardButton("Понятно", callback_data='understood')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(reply_markup=reply_markup)
    return UNDERSTOOD

# Understood handler
def understood(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Ладно еще несколько вспомогательных. Но их лучше не использовать.")
    query.message.reply_text("/new - начать новый разговор.\n/topics - выбрать какую-то тему.\n/dict Слово - Спросить определение слова.")
    query.message.reply_text("Поясню")
    query.message.reply_text("Хочешь новую тему - так и скажи 'Let's talk about the idea of an infinite universe'")
    query.message.reply_text("Не знаешь слово? Скажи 'I don't know the word 'infinite', could you explain it to me?'")
    keyboard = [[InlineKeyboardButton("Все уже ясно, может начнем", callback_data='ready')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(reply_markup=reply_markup)
    return READY

# Ready handler
def ready(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Со следующего шага я перейду на английский и больше не буду использовать русский язык:)")
    query.message.reply_text("Первое время тебе будет тяжело, но это обязательный этап обучения, со временем общаться станет легко! Главное не забрасывай наши разговоры.")
    query.message.reply_text("Дети учат язык не зная ни одного слова и у них нет возможности спросить перевода 🙂")
    keyboard = [[InlineKeyboardButton("LETSGOOO", callback_data='letsgo')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(reply_markup=reply_markup)
    return LETSGO

# Letsgo handler
def letsgo(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Hey! My Russian Alter-EGO explained you the basics. Now let's talk. Tell me about yourself?")
    # This is the end of the conversation flow. You might want to set a different state or end the conversation.
    return ConversationHandler.END


# Conversation handler setup
conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        GREET: [CallbackQueryHandler(greet, pattern='^greet$')],
        COOL: [CallbackQueryHandler(cool, pattern='^cool$')],
        TRYING: [CallbackQueryHandler(trying, pattern='^trying$')],
        UNDERSTOOD: [CallbackQueryHandler(understood, pattern='^understood$')],
        READY: [CallbackQueryHandler(ready, pattern='^ready$')],
        LETSGO: [CallbackQueryHandler(letsgo, pattern='^letsgo$')]
    },
    fallbacks=[CommandHandler('start', start)]
)
