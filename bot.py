
import logging
import re
import paramiko
import logging
import psycopg2

from psycopg2 import Error
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


TOKEN = "7183572361:AAFUbhVj5ijhza3chIkoi3ZmQ8PTfyZpTsQ"
SSH_HOST = "192.168.1.107"
SSH_UNAME = "debian"
SSH_PASSWD = "debian"
DB_USER = "postgres"
DB_PASS = "postgres"
DB_HOST = "192.168.1.107"


# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)



logger = logging.getLogger(__name__)

def split_text_into_blocks(text):
    max_block_length = 4000
    blocks = []
    current_block = ''

    # Разбиваем текст на строки
    lines = text.split('\n')

    for line in lines:
        # Проверяем, не превысит ли добавление текущей строки длину блока
        if len(current_block) + len(line) <= max_block_length:
            current_block += line + '\n'
        else:
            blocks.append(current_block)
            current_block = line + '\n'

    # Добавляем последний блок
    if current_block:
        blocks.append(current_block)

    return blocks


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')


def find_phone_numberCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'find_phone_number'

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email адресов: ')

    return 'findEmail'

# def insertEmailCommand(update: Update, context):
#     update.message.reply_text('Введите текст для поиска email адресов: ')

#     return 'insertEmail'

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки его сложности ')

    return 'verifyPassword'

def get_apt_list_command(update: Update, context):
    update.message.reply_text('Введите название пакета или all для вывода всех пакетов ')

    return 'get_apt_list'


def exec_ssh_command(command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_UNAME, password=SSH_PASSWD)
    _, ssh_stdout, _ = ssh.exec_command(command)
    return ssh_stdout.read().decode()

def get_release(update: Update, context):
    update.message.reply_text(exec_ssh_command("lsb_release -a"))

def get_uname(update: Update, context):
    update.message.reply_text(exec_ssh_command("uname -a"))

def get_uptime(update: Update, context):
    update.message.reply_text(exec_ssh_command("uptime"))

def get_df(update: Update, context):
    update.message.reply_text(exec_ssh_command("df -H"))

def get_free(update: Update, context):
    update.message.reply_text(exec_ssh_command("free"))

def get_mpstat(update: Update, context):
    update.message.reply_text(exec_ssh_command("mpstat"))

def get_w(update: Update, context):
    update.message.reply_text(exec_ssh_command("w"))

def get_auths(update: Update, context):
    update.message.reply_text(exec_ssh_command("last | head"))

def get_critical(update: Update, context):
    update.message.reply_text(exec_ssh_command("journalctl -p 2"))

def get_ps(update: Update, context):
    update.message.reply_text(exec_ssh_command("ps"))

def get_ss(update: Update, context):
    update.message.reply_text(exec_ssh_command("ss -H | head -n 35"))

def get_services(update: Update, context):
    text = exec_ssh_command("systemctl list-units --type=service")
    split_text_list = split_text_into_blocks(text)
    for block in split_text_list:
        update.message.reply_text(block)

def get_repl_logs(update: Update, context):
    text = exec_ssh_command("cat /var/log/postgresql/postgresql-15-main.log | grep repl_user")
    split_text_list = split_text_into_blocks(text)
    for block in split_text_list:
        update.message.reply_text(block)

def get_emails(update: Update, context):
    logging.basicConfig(filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, encoding="utf-8")

    connection = None
    message_text = "Emails из таблицы бд:"
    try:
        connection = psycopg2.connect(user = DB_USER,
                                    password = DB_PASS,
                                    host = DB_HOST,
                                    port = "5432", 
                                    database = "db_bot")

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM emails;")
        data = cursor.fetchall()
        for row in data:
            message_text += "\n" + row[1]

        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

    update.message.reply_text(message_text)

def get_phone_numbers(update: Update, context):
    connection = None
    message_text = "Номера телефонов из таблицы бд:"
    try:
        connection = psycopg2.connect(user = DB_USER,
                                    password = DB_PASS,
                                    host = DB_HOST,
                                    port = "5432", 
                                    database = "db_bot")

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phone_numbers;")
        data = cursor.fetchall()
        for row in data:
            message_text += "\n" + row[1]

        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

    update.message.reply_text(message_text)


def find_phone_number (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

    # Переписал регулярку для номера телефона, чтобы ловила все указанные форматы номера телефона, 
    # наверно её можно было бы оптимизировать, но мне кажется так читать намного проще.
    phoneNumRegex = re.compile(r'((\+7|8)( |-)?\(?\d{3}\)?( |-)?\d{3}( |-)?\d{2}( |-)?\d{2})')

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return # Завершаем выполнение функции
    
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i][0]}\n' # Записываем очередной номер
    update.message.reply_text(phoneNumbers + "\nХотите ли записать номера телефонов в БД (Y)?\n") # Отправляем сообщение пользователю
    context.user_data['phoneNumbers_text'] = phoneNumbers
    return "insert_phone_number" 


def insert_phone_number (update: Update, context):
    user_input = update.message.text
    phoneNumbers_list = context.user_data['phoneNumbers_text'].split('\n')

    for i in range(len(phoneNumbers_list)):
        phoneNumbers_list[i] = phoneNumbers_list[i][3::]
    phoneNumbers_list = phoneNumbers_list[:-1:]

    if user_input == "Y":
        connection = None
        # Поскольку у нас телефоны уже отбираются регуляркой, делать так достоточно безопасно. 
        sql_query = "INSERT INTO phone_numbers (number) VALUES"
        for email in phoneNumbers_list:
            sql_query = f"{sql_query}('{email}'), "
        sql_query = sql_query[:-2:] + ";"

        try:
            connection = psycopg2.connect(user = DB_USER,
                                        password = DB_PASS,
                                        host = DB_HOST,
                                        port = "5432", 
                                        database = "db_bot")

            cursor = connection.cursor()
            cursor.execute(sql_query)
            connection.commit()
            logging.info("Команда успешно выполнена")
            update.message.reply_text("Данные успешно добавлены")
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text("Ошибка при работе с PostgreSQL")
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
    
    return ConversationHandler.END  

        
def findEmail(update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) email
    
    emailRegex = re.compile(r'[\w\d\!\#\$\%\&\'\*\+\-\/\=\?\^\_\`\{\|\}\~]+@[\w\d\-]+\.\w{2,4}')

    emailList = emailRegex.findall(user_input) # Ищем email адреса

    if not emailList: 
        update.message.reply_text('Email адреса не найдены')
        return
    
    emails = '' # Создаем строку, в которую будем записывать email телефонов
    for i in range(len(emailList)):
        emails += f'{i+1}. {emailList[i]}\n' # Записываем очередной email
    update.message.reply_text(emails + "\nХотите добавить эти email в бд? (Y)") 
    context.user_data['email_text'] = emails
    return "insertEmail" 

def insertEmail(update: Update, context):
    user_input = update.message.text
    emails_list = context.user_data['email_text'].split('\n')

    for i in range(len(emails_list)):
        emails_list[i] = emails_list[i][3::]
    emails_list = emails_list[:-1:]

    if user_input == "Y":
        connection = None
        # Поскольку у нас email уже отбирается регуляркой, делать так достоточно безопасно. 
        sql_query = "INSERT INTO emails (email) VALUES"
        for email in emails_list:
            sql_query = f"{sql_query}('{email}'), "
        sql_query = sql_query[:-2:] + ";"

        try:
            connection = psycopg2.connect(user = DB_USER,
                                        password = DB_PASS,
                                        host = DB_HOST,
                                        port = "5432", 
                                        database = "db_bot")

            cursor = connection.cursor()
            cursor.execute(sql_query)
            connection.commit()
            logging.info("Команда успешно выполнена")
            update.message.reply_text("Данные успешно добавлены")
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text("Ошибка при работе с PostgreSQL")
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
    
    return ConversationHandler.END  




def verifyPassword(update: Update, context):
    user_input = update.message.text
    regexSizeBiggerEight = re.compile(r'.{8,}')  # Проверка на size > 8 символов
    regexUppercase = re.compile(r'[A-ZА-Я]') # Проверка на наличие большой буквы
    regexLowercase = re.compile(r'[a-zа-я]') # Проверка на наличие маленькой буквы
    regexDigit = re.compile(r'\d')       # Проверка на наличие одной цифры
    regexSpecialChar = re.compile(r'[\!\@\#\$\%\^\&\*\(\)\.]') # Проверка на наличие спецсимволов

    if regexSizeBiggerEight.findall(user_input) and regexUppercase.findall(user_input) and\
       regexLowercase.findall(user_input) and regexDigit.findall(user_input) and\
       regexSpecialChar.findall(user_input):
        update.message.reply_text("Пароль сложный")
    else:
        update.message.reply_text("пароль простой")
    return ConversationHandler.END       

def get_apt_list(update: Update, context):
    user_input = update.message.text
    if user_input == 'all' or user_input == "All" or user_input == "ALL":
        text = exec_ssh_command("apt list")
        split_text_list = split_text_into_blocks(text)
        for block in split_text_list:
            update.message.reply_text(block)
    else:
        update.message.reply_text(exec_ssh_command(f"apt list {user_input}"))
    return ConversationHandler.END  



def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога для поиска номера телефона
    convHandlerfind_phone_number = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_numberCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'insert_phone_number': [MessageHandler(Filters.text & ~Filters.command, insert_phone_number)],

        },
        fallbacks=[]
    )

    # Обработчик диалога для поиска email
    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('findEmail', findEmailCommand)],
        states={
            'findEmail': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
            'insertEmail': [MessageHandler(Filters.text & ~Filters.command, insertEmail)],
        },
        fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verifyPassword', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )

    convHandler_get_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_command)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )
		
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerfind_phone_number)
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(convHandler_get_apt_list)
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))







	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
