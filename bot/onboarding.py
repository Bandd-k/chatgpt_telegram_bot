from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Defining states
GREET, COOL, UNDERSTOOD, READY, LETSGO = range(5)

# Start command handler
async def start(update, context):
    keyboard = [[InlineKeyboardButton("Привет", callback_data='greet')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Привет, я бот для болтания на английском.', reply_markup=reply_markup)
    return GREET

# Greet handler
async def greet(update, context):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(text="Всем кто изучает язык не хватает языковой практики. Я буду это исправлять. Можешь говорить со мной когда захочешь и на любую тему.")
    await query.message.reply_text("Не бойся допускать ошибки, мычать, сбиваться с темы. Спрашивай абсолютно любой вопрос, переспрашивай, проси повторить!")
    keyboard = [[InlineKeyboardButton("Круто", callback_data='cool')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("У меня куча свободного времени 🙂", reply_markup=reply_markup)
    return COOL

# Cool handler
async def cool(update, context):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(text="Старайся использовать только голосовые сообщения.")
    await query.message.reply_text("Строй более сложные предложения, используй новые слова, не отвечай короткими фразами. Следи за своим произношением.")
    keyboard = [[InlineKeyboardButton("Буду стараться!", callback_data='understood')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Итоговый результат зависит только от тебя самого!", reply_markup=reply_markup)
    return UNDERSTOOD

# Understood handler
async def understood(update, context):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(text="Ладно еще несколько вспомогательных. Но их лучше не использовать.")
    await query.message.reply_text("/new - начать новый разговор.\n/topics - выбрать какую-то тему.\n/dict Слово - Спросить определение слова.")
    await query.message.reply_text("Поясню")
    await query.message.reply_text("Хочешь новую тему - так и скажи Let's talk about the idea of an infinite universe")
    keyboard = [[InlineKeyboardButton("Все уже ясно, может начнем", callback_data='ready')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Не знаешь слово? Скажи I don't know the word 'infinite', could you explain it to me?", reply_markup=reply_markup)
    return READY

# Ready handler
async def ready(update, context):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(text="Со следующего шага я перейду на английский и больше не буду использовать русский язык:)")
    await query.message.reply_text("Первое время тебе будет тяжело, но это обязательный этап обучения, со временем общаться станет легко! Главное не забрасывай наши разговоры.")
    keyboard = [[InlineKeyboardButton("LETSGOOO", callback_data='letsgo')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Дети учат язык не зная ни одного слова и у них нет возможности спросить перевода 🙂", reply_markup=reply_markup)
    return LETSGO

# Letsgo handler
async def letsgo(update, context):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(text="Hey! My Russian Alter-EGO explained you the basics. Now let's talk. Tell me about yourself?")
    # This is the end of the conversation flow. You might want to set a different state or end the conversation.
    return ConversationHandler.END


# Conversation handler setup
conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        GREET: [CallbackQueryHandler(greet, pattern='^greet$')],
        COOL: [CallbackQueryHandler(cool, pattern='^cool$')],
        UNDERSTOOD: [CallbackQueryHandler(understood, pattern='^understood$')],
        READY: [CallbackQueryHandler(ready, pattern='^ready$')],
        LETSGO: [CallbackQueryHandler(letsgo, pattern='^letsgo$')]
    },
    fallbacks=[CommandHandler('start', start)]
)
