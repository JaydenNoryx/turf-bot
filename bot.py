import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
import os
import asyncio

# 1. Webserver initialisieren
app = Flask('')

@app.route('/')
def home():
    return "Bot ist online!"

# 2. Discord Bot Klasse erstellen
class TurfBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        # Startet den Webserver asynchron direkt im Discord-Prozess
        loop = asyncio.get_running_loop()
        port = int(os.environ.get("PORT", 10000))
        loop.run_in_executor(None, lambda: app.run(host='0.0.0.0', port=port, use_reloader=False))

bot = TurfBot()

class TurfView(discord.ui.View):
    def __init__(self, gegner: str, zeit: str):
        super().__init__(timeout=None)
        self.gegner = gegner
        self.zeit = zeit
        self.spieler = []

    def generiere_embed(self) -> discord.Embed:
        embed = discord.Embed(color=discord.Color.from_rgb(139, 0, 0))
        embed.title = "⚔️ TURF"
        embed.add_field(name="🛡️ Gegner", value=f"**{self.gegner}**", inline=True)
        embed.add_field(name="⏰ Zeit", value=f"**{self.zeit}**", inline=True)
        
        liste_text = ""
        for i in range(1, 16):
            if i - 1 < len(self.spieler):
                liste_text += f"**{i}.** <@{self.spieler[i-1]}>\n"
            else:
                liste_text += f"**{i}.** Frei\n"
                
        embed.add_field(name=f"🎮 Spieler ({len(self.spieler)}/15)", value=liste_text, inline=False)
        return embed

    @discord.ui.button(label="Join", style=discord.ButtonStyle.success, emoji="✅", custom_id="turf_join")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user_id = interaction.user.id
        if user_id in self.spieler:
            await interaction.followup.send("Du bist bereits im Turf eingetragen!", ephemeral=True)
            return
        if len(self.spieler) >= 15:
            await interaction.followup.send("Der Turf ist leider schon voll! (15/15)", ephemeral=True)
            return
        self.spieler.append(user_id)
        await interaction.message.edit(embed=self.generiere_embed(), view=self)

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.danger, emoji="❌", custom_id="turf_leave")
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user_id = interaction.user.id
        if user_id not in self.spieler:
            await interaction.followup.send("Du bist gar nicht eingetragen!", ephemeral=True)
            return
        self.spieler.remove(user_id)
        await interaction.message.edit(embed=self.generiere_embed(), view=self)

@bot.tree.command(name="turf", description="Startet eine neue Turf-Anmeldung.")
@app_commands.describe(gegner="Gegen welche Familie wird gekämpft?", zeit="Wann startet der Turf? (z.B. 18:00)")
async def turf(interaction: discord.Interaction, gegner: str, zeit: str):
    await interaction.response.defer()
    view = TurfView(gegner, zeit)
    msg_text = "<@&1186401035300905021> Ein neues Turf startet!"
    await interaction.followup.send(content=msg_text, embed=view.generiere_embed(), view=view)

# Bot starten mit deinem Token
bot.run("MTUwNjczMjQ1NjEwMTk0MTQ3OQ.GaVlAh.IbYwVOz6Gv84S9FTisjtgI7-jqg_ggJv8ugWwI")
