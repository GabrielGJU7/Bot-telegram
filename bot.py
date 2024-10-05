import logging
import requests
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler
import asyncio

# Configurar el bot y logging
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
NEWS_API_KEY = 'YOUR_NEWS_API_KEY'  # Usa una API como NewsAPI
CHAT_ID = 'YOUR_CHAT_ID'  # El chat ID donde se enviarán las noticias

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Función para obtener noticias de fútbol
def get_football_news():
    url = f"https://newsapi.org/v2/everything?q=football&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    news_data = response.json()

    if news_data['status'] == 'ok':
        articles = news_data['articles'][:5]  # Limitar a las 5 primeras noticias
        return articles
    else:
        return []

# Función para enviar noticias al chat de Telegram
async def send_news(application: Application):
    news_list = get_football_news()
    if news_list:
        for news in news_list:
            title = news['title']
            description = news['description']
            url = news['url']
            image_url = news.get('urlToImage')

            # Descargar la imagen
            if image_url:
                try:
                    await application.bot.send_photo(chat_id=CHAT_ID, photo=image_url, caption=f"{title}\n\n{description}\n{url}")
                except Exception as e:
                    logger.error(f"Error al descargar la imagen: {e}")
            else:
                await application.bot.send_message(chat_id=CHAT_ID, text=f"{title}\n\n{description}\n{url}")
    else:
        await application.bot.send_message(chat_id=CHAT_ID, text="No hay noticias de fútbol disponibles en este momento.")

# Comando /start para iniciar el bot
async def start(update: Update, context):
    await update.message.reply_text('¡Bot de noticias de fútbol activado! Te enviaré noticias cada hora.')

# Tarea periódica para enviar las noticias cada hora
async def periodic_news_sender(application: Application):
    while True:
        await send_news(application)
        await asyncio.sleep(3600)  # Espera de 1 hora (3600 segundos)

# Función principal
async def main():
    # Crear la aplicación de Telegram con el token
    application = Application.builder().token(TOKEN).build()

    # Registrar el comando /start
    application.add_handler(CommandHandler("start", start))

    # Programar el envío de noticias periódicas
    asyncio.create_task(periodic_news_sender(application))

    # Ejecutar el bot
    await application.start_polling()

    # Mantener el bot ejecutándose
    await application.idle()

if __name__ == '__main__':
    asyncio.run(main())
