from discord.ext import commands
from discord import app_commands
import discord
import os 
from dotenv import load_dotenv
import requests
import json
load_dotenv()

CHANNEL_ID = "None"
api = os.getenv("discord_api_secret")
faceit = os.getenv("faceit_api")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
headers = {"Authorization": f"Bearer {faceit}",
           "Content-type": "application/json"
    
}

levels = [(901,1050),(1051,1200),(1201,1350),(1351,1530),(1531,1750),(1751,2000),(2001,4000)]

def get_elo_needed(elo):
    for index, level in enumerate(levels):
        if elo >= level[0] and elo <= level[1]:
           val= (level[1] - elo + 1), index + 4 + 1
           elo_gained = val[0]
           return elo_gained
        if elo > 2001:
            return("top 500 incoming")
    return(False, False)

def get_next_level(elo):
    for index, level in enumerate(levels):
        if elo >= level[0] and elo <= level[1]:
           val= (level[1] - elo + 1), index + 4 + 1
           elo_gained = val[1]
           return elo_gained
        if elo > 2001:
            return("top 500 incoming")
    return(False, False)

def get_playerid(user):
    response= requests.get(f"https://open.faceit.com/data/v4/players?nickname={user}", headers=headers)
    if response.status_code == 200:
        player_id = response.json()["player_id"]
        return player_id
    else:
        print("Error", response.text)
        return None
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Error: {error}")
        
@bot.event
async def on_ready():
    print("Bot Online....")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Bot Online....")
    try:
        sycned = await bot.tree.sync()
        print(f"Synced {len(sycned)} commands(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="faceit_info")
async def faceit_info(interaction: discord.Interaction, get_user: str):
    link = requests.get(f"https://open.faceit.com/data/v4/players?nickname={get_user}", headers=headers)
    if link.status_code == 200:
        response = link.text
        data = json.loads(response)
        elo = data["games"]["cs2"]["faceit_elo"]
        skill_level = data["games"]["cs2"]["skill_level"]

        int_elo = int(elo)

        embed = discord.Embed(
            color=discord.Color.dark_orange(),
            description="Faceit user info",
            title="FACEIT"

        )

        get_elo = get_elo_needed(int_elo)
        next_level = get_next_level(int_elo)
        imageurl = "https://yt3.googleusercontent.com/TS0smYzk2Z06eT60nbF9Nf49PpDn-zSQjoSYHKXE2EgTk4LDUFKWvq70vrw7PlL-KY59oUTkEA=s900-c-k-c0x00ffffff-no-rj"
        embed.set_footer(text=f"Faceit user:{get_user}\nYour elo is: {elo}\nSkill level is: Lvl({skill_level})\nElo needed to rank up: {get_elo}\nNext level is: {next_level}")
        embed.set_thumbnail(url = imageurl)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"Error: [{get_user}] does not exist")

@faceit_info.error
async def stats_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("!stats needs a argument....")


@bot.tree.command(name="faceit_kd")
async def faceit_kd(interaction: discord.Interaction, get_user: str):
    faceit_playerid = get_playerid(get_user)
    link = requests.get(f"https://open.faceit.com/data/v4/players/{faceit_playerid}/stats/cs2", headers=headers)
    if link.status_code == 200:
            response = link.text
            data = json.loads(response)
            kd = data["lifetime"]["Average K/D Ratio"]
            embed = discord.Embed(
                color=discord.Color.dark_orange(),
                description="FACEIT average K/D",
                title="FACEIT"
            )
            imageurl = "https://yt3.googleusercontent.com/TS0smYzk2Z06eT60nbF9Nf49PpDn-zSQjoSYHKXE2EgTk4LDUFKWvq70vrw7PlL-KY59oUTkEA=s900-c-k-c0x00ffffff-no-rj"
            embed.set_footer(text=f"{get_user}'s average KD is: {kd}")
            embed.set_thumbnail(url = imageurl)
            await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"{get_user} does not exist")

@faceit_kd.error
async def faceitkd_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("!kd needs a argument....")

@bot.tree.command(name="faceit_kills")
async def faceit_kills(interaction: discord.Interaction, get_user: str):
    faceit_playerid = get_playerid(get_user)
    response = requests.get(f"https://open.faceit.com/data/v4/players/{faceit_playerid}/games/cs2/stats?offset=0&limit=10", headers=headers)
    data = json.loads(response.text)
    try:
        if response.status_code == 200:
            all_kills = []
            for item in data['items']:
                kills = item['stats']['Kills']
                all_kills.append(int(kills))
            average = sum(all_kills)/len(all_kills)
            average_kd = []
            for item in data['items']:
                kd = item['stats']['K/D Ratio']
                average_kd.append(float(kd))
            kd_average = sum(average_kd)/len(average_kd)
            avg_kd = format(kd_average, ".2f")
            embed = discord.Embed(
                color=discord.Color.dark_orange(),
                description="FACEIT average kills & K/D for past 10 games",
                title="FACEIT"
            )
            imageurl = "https://yt3.googleusercontent.com/TS0smYzk2Z06eT60nbF9Nf49PpDn-zSQjoSYHKXE2EgTk4LDUFKWvq70vrw7PlL-KY59oUTkEA=s900-c-k-c0x00ffffff-no-rj"
            embed.set_footer(text=f"{get_user}'s average kills for the past 10 games are: {average}\n{get_user}'s average K/D for the past 10 games: {avg_kd}")
            embed.set_thumbnail(url=imageurl)
            await interaction.response.send_message(embed=embed)
    except ZeroDivisionError:
        await interaction.response.send_message("Something went wrong either user doesn't exist or stats were unretreivable")
@faceit_kills.error
async def faceitkills_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Add a argument please")
        

@bot.tree.command(name="best_map")
async def best_map(interaction: discord.Interaction, get_user: str):
    faceit_playerid = get_playerid(get_user)
    response = requests.get(f"https://open.faceit.com/data/v4/players/{faceit_playerid}/stats/cs2", headers=headers)
    data = json.loads(response.text)
    if response.status_code == 200:
        all_maps = []   
        map_percentage = []
        matches_played = []
        matches_list = [] 
        for item in data['segments']:
            map = item['label']
            all_maps.append(map)
            win_percentage = item['stats']['Win Rate %']
            map_percentage.append(int(win_percentage))
            matches = item["stats"]["Matches"]
            matches_played.append(int(matches))
        for m, mp, ma in zip(all_maps, matches_played, map_percentage):
            stats = {'map': m, 'matches': mp, "map percentage": ma}
            matches_list.append(stats)      
           
        res = [i for i in matches_list if not (i["matches"] < 5)]

        filitred_result = max(res, key=lambda x:x['map percentage'])
        map = filitred_result['map']
        percentage = filitred_result['map percentage']
        embed = discord.Embed(
            description=f"{get_user}'s bestmap",
            color=discord.Color.dark_orange(),
            title="FACEIT"
        )
        imageurl = "https://yt3.googleusercontent.com/TS0smYzk2Z06eT60nbF9Nf49PpDn-zSQjoSYHKXE2EgTk4LDUFKWvq70vrw7PlL-KY59oUTkEA=s900-c-k-c0x00ffffff-no-rj"
        embed.set_footer(text=f"Best map is: {map}\nWin percentage: {percentage}%")
        embed.set_thumbnail(url=imageurl)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"{get_user} does not exist")     
bot.run(api)