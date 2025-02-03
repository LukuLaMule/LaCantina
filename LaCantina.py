import os
import discord
import requests
import asyncio
from pdf2image import convert_from_path
from PIL import Image

# Charger les variables d'environnement
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_IDS = [
    int(os.getenv('CHANNEL_ID_1')),
    int(os.getenv('CHANNEL_ID_2'))
]

# Vérification des variables d'environnement
if not TOKEN:
    raise ValueError("Le token Discord n'est pas défini dans l'environnement.")
if not CHANNEL_IDS or None in CHANNEL_IDS:
    raise ValueError("Un ou plusieurs Channel IDs ne sont pas définis dans l'environnement.")

# Initialisation du bot avec les intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Fonction pour télécharger le PDF
def download_pdf(url, save_path):
    print("Téléchargement du PDF...")
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)
    print("PDF téléchargé.")

# Fonction pour convertir la première page du PDF en image
def pdf_to_image(pdf_path, image_path):
    print("Conversion du PDF en image...")
    try:
        poppler_path = '/usr/bin'  # Modifier si nécessaire
        images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path=poppler_path)
        images[0].save(image_path, 'PNG')
        print("Image enregistrée.")
    except Exception as e:
        print(f"Erreur lors de la conversion PDF -> Image : {e}")

# Fonction pour envoyer l'image dans un seul channel (où la commande a été reçue)
async def send_image(channel, image_path):
    print(f"Envoi de l'image dans le channel {channel.id}...")
    with open(image_path, 'rb') as f:
        await channel.send("Voici le menu de la semaine !", file=discord.File(f, image_path))
    print("Image envoyée.")

# Vérification périodique des mises à jour
async def check_for_updates():
    await client.wait_until_ready()
    last_modified_date = None

    while True:
        print("Vérification des mises à jour...")
        response = requests.head("https://webdfd.mines-ales.fr/restau/Menu_Semaine.pdf")
        current_last_modified = response.headers.get('Last-Modified')

        if current_last_modified and current_last_modified != last_modified_date:
            print("Le menu a été mis à jour !")
            last_modified_date = current_last_modified

            pdf_save_path = 'Menu_Semaine.pdf'
            image_save_path = 'Menu_Semaine.png'
            download_pdf("https://webdfd.mines-ales.fr/restau/Menu_Semaine.pdf", pdf_save_path)
            pdf_to_image(pdf_save_path, image_save_path)

            # Envoyer l'image à tous les channels configurés (mise à jour auto)
            for channel_id in CHANNEL_IDS:
                channel = client.get_channel(channel_id)
                if channel:
                    await send_image(channel, image_save_path)

        await asyncio.sleep(3600)  # Vérifie toutes les heures

# Événement quand le bot est prêt
@client.event
async def on_ready():
    print(f'Connecté en tant que {client.user}')

# Événement pour gérer la commande !menu
@client.event
async def on_message(message):
    if message.content == '!menu' and not message.author.bot:  # Empêcher le bot de répondre à lui-même
        print(f"Commande '!menu' reçue de {message.author} dans {message.channel.id}")

        pdf_save_path = 'Menu_Semaine.pdf'
        image_save_path = 'Menu_Semaine.png'

        # Télécharger et convertir le menu
        download_pdf("https://webdfd.mines-ales.fr/restau/Menu_Semaine.pdf", pdf_save_path)
        pdf_to_image(pdf_save_path, image_save_path)

        # Envoyer uniquement dans le channel où la commande a été reçue
        await send_image(message.channel, image_save_path)

# Fonction principale pour exécuter le bot
async def main():
    async with client:
        client.loop.create_task(check_for_updates())  # Vérifie périodiquement les mises à jour
        await client.start(TOKEN)

# Lancer le bot
asyncio.run(main())

