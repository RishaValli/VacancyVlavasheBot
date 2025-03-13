import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Ваш ID (замените на ваш реальный ID)
ADMIN_ID = 701763164  # Пример ID, замените на ваш

# Состояния для ConversationHandler
SELECT_VACANCY, SHOW_DESCRIPTION, NAME, AGE, EXPERIENCE, SCHEDULE, CITIZENSHIP, PHONE, METRO, MEDICAL_BOOK, PHOTO, RESUME = range(12)

# Список вакансий
vacancies = {
    "Администратор-кассир": "Описание администратора-кассира...",
    "Кассир-бариста": "Описание кассира-баристы...",
    "Старший повар": "Описание старшего повара...",
    "Повар": "Описание повара...",
    "Работник кухни": "Описание работника кухни...",
}

# Проверка номера телефона
def is_valid_phone(phone: str) -> bool:
    return re.match(r"^\+7\d{10}$", phone) is not None

# Основной обработчик
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привет! 👋 Рады, что вы заинтересовались работой в нашей команде. "
        "Пожалуйста, выберите вакансию, которая вас заинтересовала:",
        reply_markup=ReplyKeyboardMarkup([[vacancy] for vacancy in vacancies.keys()], one_time_keyboard=True)
    )
    return SELECT_VACANCY

# Выбор вакансии
async def select_vacancy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_vacancy = update.message.text
    context.user_data['vacancy'] = selected_vacancy

    # Показываем описание вакансии и кнопки "Откликнуться" и "Назад"
    await update.message.reply_text(
        f"Вакансия: {selected_vacancy}\n"
        f"Описание: {vacancies[selected_vacancy]}\n\n"
        "Хотите откликнуться на эту вакансию?",
        reply_markup=ReplyKeyboardMarkup([["Откликнуться", "Назад"]], one_time_keyboard=True)
    )
    return SHOW_DESCRIPTION

# Обработка кнопок "Откликнуться" и "Назад"
async def show_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_response = update.message.text

    if user_response == "Назад":
        await update.message.reply_text(
            "Выберите вакансию:",
            reply_markup=ReplyKeyboardMarkup([[vacancy] for vacancy in vacancies.keys()], one_time_keyboard=True)
        )
        return SELECT_VACANCY
    elif user_response == "Откликнуться":
        await update.message.reply_text("Как вас зовут?")
        return NAME
    else:
        await update.message.reply_text("Пожалуйста, используйте кнопки.")
        return SHOW_DESCRIPTION

# Вопрос о имени
async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Сколько вам лет?")
    return AGE

# Вопрос о возрасте
async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        age = int(update.message.text)  # Пробуем преобразовать в число
        context.user_data['age'] = age
        await update.message.reply_text("Какой у вас опыт?", reply_markup=ReplyKeyboardMarkup([["Опыта нет, но есть желание", "Менее 1 года"], ["1-2 года", "Более 2 лет"]], one_time_keyboard=True))
        return EXPERIENCE
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите возраст числом (например, 25).")
        return AGE

# Вопрос о опыте
async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['experience'] = update.message.text
    await update.message.reply_text("Какой график вы рассматриваете для себя в приоритете?", reply_markup=ReplyKeyboardMarkup([["2/2", "5/2"], ["6/1", "по выходным", "другой"]], one_time_keyboard=True))
    return SCHEDULE

# Вопрос о графике
async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['schedule'] = update.message.text
    await update.message.reply_text("Какое у вас гражданство?")
    return CITIZENSHIP

# Вопрос о гражданстве
async def citizenship(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['citizenship'] = update.message.text
    await update.message.reply_text("Ваш номер телефона (начинается с +7):")
    return PHONE

# Вопрос о номере телефона
async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone = update.message.text
    if not is_valid_phone(phone):
        await update.message.reply_text("Номер телефона должен начинаться с +7 и содержать 11 цифр. Пожалуйста, введите номер еще раз.")
        return PHONE
    context.user_data['phone'] = phone
    await update.message.reply_text("Рядом с какой станцией метро вы проживаете?")
    return METRO

# Вопрос о метро
async def metro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['metro'] = update.message.text
    await update.message.reply_text("Есть ли у вас медкнижка (действующая)?", reply_markup=ReplyKeyboardMarkup([["да", "нет"]], one_time_keyboard=True))
    return MEDICAL_BOOK

# Вопрос о медкнижке
async def medical_book(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['medical_book'] = update.message.text
    await update.message.reply_text("Загрузите, пожалуйста, ваше фото.")
    return PHOTO

# Вопрос о фото
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['photo'] = update.message.photo[-1].file_id  # Сохраняем file_id фото
    await update.message.reply_text("Загрузите, пожалуйста, ваше резюме (если есть).", reply_markup=ReplyKeyboardMarkup([["Загрузить резюме", "Нет резюме"]], one_time_keyboard=True))
    return RESUME

# Вопрос о резюме
async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.document:  # Если загружен документ
        context.user_data['resume'] = update.message.document.file_id  # Сохраняем file_id резюме
    elif update.message.text == "Нет резюме":  # Если пользователь нажал "Нет резюме"
        context.user_data['resume'] = None
    else:
        await update.message.reply_text("Пожалуйста, загрузите резюме или нажмите 'Нет резюме'.")
        return RESUME

    # Отправка резюме в личные сообщения
    await context.bot.send_message(
        chat_id=ADMIN_ID,  # Ваш ID
        text=f"Новое резюме:\n"
             f"Вакансия: {context.user_data['vacancy']}\n"
             f"Имя: {context.user_data['name']}\n"
             f"Возраст: {context.user_data['age']}\n"
             f"Опыт: {context.user_data['experience']}\n"
             f"График: {context.user_data['schedule']}\n"
             f"Гражданство: {context.user_data['citizenship']}\n"
             f"Телефон: {context.user_data['phone']}\n"
             f"Метро: {context.user_data['metro']}\n"
             f"Медкнижка: {context.user_data['medical_book']}\n"
             f"Резюме: {'Загружено' if context.user_data['resume'] else 'Отсутствует'}"
    )

    # Отправка фото
    await context.bot.send_photo(
        chat_id=ADMIN_ID,  # Ваш ID
        photo=context.user_data['photo'],
        caption="Фото кандидата"
    )

    # Отправка резюме (если загружено)
    if context.user_data['resume']:
        await context.bot.send_document(
            chat_id=ADMIN_ID,  # Ваш ID
            document=context.user_data['resume'],
            caption="Резюме кандидата"
        )

    context.user_data.clear()
    await update.message.reply_text("Спасибо! Ваше резюме отправлено.")
    return ConversationHandler.END

# Команда /my_id
async def my_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    await update.message.reply_text(f"Ваш ID: {user_id}")

def main() -> None:
    # Создаем приложение
    application = Application.builder().token("7695919804:AAFoM8xFzyrLHPxvvnvusAFzf_7PR1Tdgno").build()

    # Обработчик для команды /my_id
    application.add_handler(CommandHandler("my_id", my_id))

    # Обработчик для основного функционала
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_VACANCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_vacancy)],
            SHOW_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, show_description)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience)],
            SCHEDULE: [MessageHandler(filters.TEXT & ~filters.COMMAND, schedule)],
            CITIZENSHIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, citizenship)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            METRO: [MessageHandler(filters.TEXT & ~filters.COMMAND, metro)],
            MEDICAL_BOOK: [MessageHandler(filters.TEXT & ~filters.COMMAND, medical_book)],
            PHOTO: [MessageHandler(filters.PHOTO, photo)],
            RESUME: [MessageHandler(filters.TEXT | filters.Document.MimeType("application/pdf"), resume)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()