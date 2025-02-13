
import discord
import json
import random
import os

# Define the intents
intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = discord.app_commands.CommandTree(client)

#Global variables
token = "#[Add your discord token here]"
app_id = "1280472482968637471"
guild = discord.Object(id=1279200089440780382)

# Save character data to the json file
def save_character(char_name, modifiers):
    char = {'name': char_name, 'stats': modifiers}
    character.append(char)
    with open('character.json', 'w') as f:
        json.dump(character, f, indent=4)

# Save notes data to the json file
def save_note(note_title, note_description):
    new_note = {'title': note_title, 'description': note_description}
    notes.append(new_note)
    with open('notes.json', 'w') as f:
        json.dump(notes, f, indent=4)

# Load existing character data if it exists
if os.path.exists('character.json'):
    with open('character.json', 'r') as f:
        character = json.load(f)
else:
    character = []

# Load existing notes data if it exists
if os.path.exists('notes.json'):
    with open('notes.json', 'r') as f:
        notes = json.load(f)
else:
    notes = []

#Search function
def search(dict_list, search_string):
    return [d for d in dict_list if search_string in d.values()]

# OOC slash command to send out of character messages
@bot.command(name="ooc", description="Send an out of character message", guild=guild)
async def ooc(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(f"OOC: {interaction.user.name}: {message}")

# Slash command to create a character
@bot.command(name="create_character", description="Create a new character", guild=guild)
async def create_character(interaction: discord.Interaction):
    if len(character) > 0:
        await interaction.response.send_message("You already have a character created. Use command '/show_character' to display info.", ephemeral=True)
        return
    
    def check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel

    await interaction.response.send_message('What is your character’s name?', ephemeral=True)
    
    try:
        msg = await client.wait_for('message', check=check, timeout=60)
        char_name = msg.content
    except:
        await interaction.followup.send("Character creation timed out.", ephemeral=True)
        return

    stats = ['Adaptability', 'Boldness', 'Critical Thinking', 'Empathy']
    modifiers = {}

    for stat in stats:
        await interaction.followup.send(f'Please enter your {stat} modifier:', ephemeral=True)
    

        try:
            msg = await client.wait_for('message', check=check, timeout=60)
            modifiers[stat] = int(msg.content)
            # if modifiers[stat] < -3 or modifiers[stat] > 3:
            #     await interaction.followup.send("modifier needs to be between -3 and 3.")
        except:
            await interaction.followup.send("Character creation timed out.", ephemeral=True)
            return

    # Save character to json
    save_character(char_name, modifiers)

    await interaction.followup.send(f"Character **{char_name}** has been created!", ephemeral=True)

# Slash command to show character info
@bot.command(name="show_character", description="Display your character sheet", guild=guild)
async def show_character(interaction: discord.Interaction):
    if len(character) == 0:
        await interaction.response.send_message("You don't have a character created.", ephemeral=True)
        return

    embed = discord.Embed(title=f"{character[0]['name']}'s Character Sheet")

    for stat, modifier in character[0]['stats'].items():
        embed.add_field(name=stat, value=str(modifier), inline=False)

    await interaction.response.send_message(embed=embed)

# Slash command to create a note
@bot.command(name="create_note", description="Create a new note", guild=guild)
async def create_note(interaction: discord.Interaction):
    def check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel
    
    await interaction.response.send_message("What is the title of your note?", ephemeral=True)

    try:
        msg = await client.wait_for('message', check=check, timeout=60)
        note_title = msg.content
    except:
        await interaction.followup.send("Note creation timed out.", ephemeral=True)
        return
    
    await interaction.followup.send("Enter note description", ephemeral=True)

    try:
        msg = await client.wait_for("message", check=check, timeout=200)
        note_description = msg.content
    except:
        await interaction.followup.send("Note creation timed out.", ephemeral=True)
        return
    
    #Save note to json
    save_note(note_title, note_description)

    await interaction.followup.send(f"Note **{note_title}** has been created!", ephemeral=True)

#Slash command to show all notes
@bot.command(name="show_notes", description="Display your notes", guild=guild)
async def show_notes(interaction: discord.Interaction):    
    if len(notes) == 0:
        await interaction.response.send_message("You don't have any notes created.", ephemeral=True)
        return
    delimiter = '\n'
    embed = discord.Embed(title=f"{interaction.user}'s Notes", description=f"**{delimiter.join([note['title'] for note in notes])}**")
    
    await interaction.response.send_message(embed=embed)

# Slash command to show note by title
@bot.command(name="show_note", description="Show specific note by title", guild=guild)
async def show_note(interaction: discord.Interaction, title: str): 
    if len(notes) == 0:
        await interaction.response.send_message("You don't have any notes created.", ephemeral=True)
        return
   
    res = search(notes, title)
    
    if res == []:
        await interaction.response.send_message(f"Title **{title}** does not exist.", ephemeral= True)
    else:
        embed = discord.Embed(title=res[0]['title'], description=res[0]['description'])
        await interaction.response.send_message(embed=embed)
        

# Slash command to roll a stat
@bot.command(name="roll", description="Roll a stat", guild=guild)
async def roll(interaction: discord.Interaction, stat: str):
    if len(character) == 0:
        await interaction.response.send_message("You don't have a character created.", ephemeral=True)
        return

    if stat not in character[0]['stats']:
        await interaction.response.send_message(f"Stat '{stat}' does not exist.", ephemeral=True)
        return

    modifier = character[0]['stats'][stat]
    roll_result = random.randint(1, 6) + random.randint(1, 6) + modifier
    await interaction.response.send_message(f"**{character[0]['name']}** rolled **{roll_result}** for {stat}!")

# Slash command to send GM message in an embed
@bot.command(name="gm", description="Send a GM message in the chat", guild=guild)
async def gm(interaction: discord.Interaction, message: str):
    embed = discord.Embed(title="GM", description=message, color=discord.Color.red())
    await interaction.response.send_message(embed=embed)

# Sync the commands with Discord
@client.event
async def on_ready():    
    await bot.sync(guild=guild)
    # print(f"{client.user.name} is ready!")
    await client.get_channel(1279200089440780385).send("I'm ready to work!")

# Running the Bot
client.run(token)
