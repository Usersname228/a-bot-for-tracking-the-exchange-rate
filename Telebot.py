import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
import json
from datetime import datetime

BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = telebot.TeleBot(BOT_TOKEN)

def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button1 = KeyboardButton('💰 Курсы валют')
    button2 = KeyboardButton('📈 Криптовалюты')
    button3 = KeyboardButton('ℹ️ О боте')
    keyboard.add(button1, button2, button3)
    return keyboard

def get_currency_rates():
    """
    Получение курсов валют из разных источников
    """
    try:
        # Основной источник - ЦБ РФ
        cbr_url = 'https://www.cbr-xml-daily.ru/daily_json.js'
        response = requests.get(cbr_url, timeout=10)
        data = response.json()
        
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        # Формируем сообщение с курсами
        result = f"*💵 КУРСЫ ВАЛЮТ* \n*Время:* {current_time}\n\n"
        result += "*Основные валюты:*\n"
        
        # Основные валюты
        currencies = {
            'USD': '🇺🇸 Доллар США',
            'EUR': '🇪🇺 Евро', 
            'CNY': '🇨🇳 Китайский юань',
            'GBP': '🇬🇧 Фунт стерлингов',
            'JPY': '🇯🇵 Японская иена',
            'CHF': '🇨🇭 Швейцарский франк'
        }
        
        for code, name in currencies.items():
            if code in data['Valute']:
                value = data['Valute'][code]['Value']
                previous = data['Valute'][code]['Previous']
                change = value - previous
                change_icon = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                result += f"{name}: *{value:.2f}₽* {change_icon}\n"
        
        result += f"\n_Данные ЦБ РФ, обновление: {current_time}_"
        
        return result
        
    except Exception as e:
        return f"❌ *Не удалось получить данные*\nОшибка: {str(e)}"

def get_crypto_rates():
    """
    Получение курсов криптовалют
    """
    try:
        # API для криптовалют
        crypto_url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=rub,usd'
        response = requests.get(crypto_url, timeout=10)
        data = response.json()
        
        result = "*💰 КРИПТОВАЛЮТЫ*\n\n"
        
        if 'bitcoin' in data:
            btc_rub = data['bitcoin']['rub']
            btc_usd = data['bitcoin']['usd']
            result += f"*Bitcoin (BTC)*\n"
            result += f"🇺🇸 ${btc_usd:,.0f}\n"
            result += f"🇷🇺 {btc_rub:,.0f}₽\n\n"
        
        if 'ethereum' in data:
            eth_rub = data['ethereum']['rub']
            eth_usd = data['ethereum']['usd']
            result += f"*Ethereum (ETH)*\n"
            result += f"🇺🇸 ${eth_usd:,.0f}\n"
            result += f"🇷🇺 {eth_rub:,.0f}₽\n"
        
        result += f"\n_Данные: CoinGecko_"
        
        return result
        
    except:
        return "*❌ Не удалось получить данные о криптовалютах*"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
*💱 Бот финансовых курсов*

📊 *Получайте актуальные курсы:*
• 💰 Валюты ЦБ РФ
• 📈 Криптовалюты

Используйте кнопки ниже ⬇️
"""
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        parse_mode='Markdown',
        reply_markup=create_main_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == '💰 Курсы валют')
def handle_currency_rates(message):
    bot.send_message(message.chat.id, "🔄 Получаю актуальные курсы...")
    rates = get_currency_rates()
    bot.send_message(
        message.chat.id, 
        rates, 
        parse_mode='Markdown',
        reply_markup=create_main_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == '📈 Криптовалюты')
def handle_crypto_rates(message):
    bot.send_message(message.chat.id, "🔄 Получаю курсы криптовалют...")
    rates = get_crypto_rates()
    bot.send_message(
        message.chat.id, 
        rates, 
        parse_mode='Markdown',
        reply_markup=create_main_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == 'ℹ️ О боте')
def handle_about(message):
    about_text = """
*🤖 О боте*

*Функции:*
• 💰 Курсы валют ЦБ РФ
• 📈 Курсы криптовалют
• ⏰ Автоматическое обновление

*Источники данных:*
• Центральный Банк РФ
• CoinGecko API

*Команды:*
/start - Запустить бота
/rates - Курсы валют

_Бот создан для демонстрации возможностей_
"""
    bot.send_message(
        message.chat.id, 
        about_text, 
        parse_mode='Markdown',
        reply_markup=create_main_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    bot.send_message(
        message.chat.id, 
        "Выберите действие с помощью кнопок ниже 👇",
        reply_markup=create_main_keyboard()
    )

if __name__ == "__main__":
    print("💰 Бот курсов валют запущен и готов к работе!")
    bot.polling(none_stop=True)
