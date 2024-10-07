import discord
import requests
import asyncio
from pdf2image import convert_from_path
from PIL import Image

# Discord bot token
TOKEN = 'Discord Token Bot'

# URL of the menu PDF
PDF_URL = 'https://webdfd.mines-ales.fr/restau/Menu_Semaine.pdf'

# Variable to store the last modified date
last_modified_date = None

# Enabling Intents
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content for commands

client = discord.Client(intents=intents)

# Function to download the PDF from the URL
def download_pdf(url, save_path):
    print("Downloading PDF...")
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)
    print("PDF downloaded.")

# Function to convert the first page of the PDF to an image
def pdf_to_image(pdf_path, image_path):
    print("Converting PDF to image...")
    try:
        poppler_path = '/usr/bin'  # Modify this path if Poppler isn't in the system's PATH
        images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path=poppler_path)
        images[0].save(image_path, 'PNG')
        print("Image saved.")
    except Exception as e:
        print(f"Error during PDF to image conversion: {e}")

# Function to send the image to the Discord channels
async def send_image_to_channels(channel_ids, image_path):
    print("Sending image to Discord channels...")
    for channel_id in channel_ids:
        channel = client.get_channel(channel_id)
        if channel:
            with open(image_path, 'rb') as f:
                await channel.send("Voici le menu de la semana !", file=discord.File(f, image_path))
            print(f"Image sent to channel {channel_id}.")
        else:
            print(f"Channel with ID {channel_id} not found.")

# Function to check the last modified date of the PDF file
def get_last_modified(url):
    response = requests.head(url)
    if 'Last-Modified' in response.headers:
        return response.headers['Last-Modified']
    return None

# Periodically check for updates
async def check_for_updates(channel_ids):
    global last_modified_date
    await client.wait_until_ready()

    while True:
        print("Checking for updates...")
        current_last_modified = get_last_modified(PDF_URL)

        # If the file has been modified since the last check, send the new menu
        if current_last_modified and current_last_modified != last_modified_date:
            print("LE MENU DE LA SEMAINE, AHHH VWAIMENT !")
            last_modified_date = current_last_modified  # Update the last modified date

            # Download the new menu
            pdf_save_path = 'Menu_Semaine.pdf'
            image_save_path = 'Menu_Semaine.png'
            download_pdf(PDF_URL, pdf_save_path)

            # Convert the first page to an image and send it to all channels
            pdf_to_image(pdf_save_path, image_save_path)
            await send_image_to_channels(channel_ids, image_save_path)

        # Wait for an hour before checking again
        await asyncio.sleep(3600)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# Event listener for message commands
@client.event
async def on_message(message):
    if message.content == '!menu':  # Manually trigger the menu anytime
        print(f"Command '!menu' received from {message.author}.")
        
        pdf_save_path = 'Menu_Semaine.pdf'
        image_save_path = 'Menu_Semaine.png'

        # Download the PDF
        download_pdf(PDF_URL, pdf_save_path)

        # Convert the first page of the PDF to an image
        pdf_to_image(pdf_save_path, image_save_path)

        # Send the image to the channel
        await send_image_to_channels([message.channel.id], image_save_path)

# Main function to run the bot
async def main():
    # List of channel IDs to send the menu to
    channel_ids = [1242463472437166174, 1016473408164339772]  # Replace CHANNEL_ID_2 with the actual second channel ID

    async with client:
        client.loop.create_task(check_for_updates(channel_ids))  # Periodically check for updates in the background
        await client.start(TOKEN)

# Run the bot
asyncio.run(main())