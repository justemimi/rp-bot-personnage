from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Je suis en vie !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

import discord
from discord.ext import commands
import json
import os

# Charger ou initialiser les personnages
if os.path.exists("data.json"):
    with open("data.json", "r") as f:
        personnages = json.load(f)
else:
    personnages = {}

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="m!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} est connecté avec succès !")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    for nom, infos in personnages.items():
        if message.content.startswith(infos['symbole']):
            if infos.get("restreint", False):
                allowed_roles = infos.get("roles", [])
                if not any(role.id in allowed_roles for role in message.author.roles):
                    await message.channel.send(f"Tu n'as pas la permission d'utiliser {nom}.")
                    return

            webhooks = await message.channel.webhooks()
            webhook = None
            for w in webhooks:
                if w.name == "PersonnagesWebhook":
                    webhook = w
                    break
            if webhook is None:
                webhook = await message.channel.create_webhook(name="PersonnagesWebhook")

            contenu = message.content[len(infos['symbole']):].strip()

            try:
                if infos.get("image_url"):
                    await webhook.send(
                        contenu,
                        username=nom,
                        avatar_url=infos['image_url']
                    )
                else:
                    await webhook.send(
                        contenu,
                        username=nom
                    )
                await message.delete()
            except Exception as e:
                print(f"Erreur webhook: {e}")
            break

    await bot.process_commands(message)

def sauvegarder():
    with open("data.json", "w") as f:
        json.dump(personnages, f, indent=4)

@bot.command(name="create")
async def create(ctx, nom: str, symbole: str, *, type_perso: str):
    personnages[nom] = {
        "symbole": symbole,
        "type": type_perso,
        "restreint": False,
        "roles": [],
        "image_url": None
    }
    sauvegarder()
    await ctx.send(f"Personnage **{nom}** créé avec le symbole **{symbole}** et type **{type_perso}** !")

@bot.command(name="modifier_nom")
async def modifier_nom(ctx, ancien_nom: str, nouveau_nom: str):
    if ancien_nom not in personnages:
        await ctx.send("Personnage non trouvé.")
        return
    personnages[nouveau_nom] = personnages.pop(ancien_nom)
    sauvegarder()
    await ctx.send(f"Nom modifié : **{ancien_nom}** ➔ **{nouveau_nom}**.")

@bot.command(name="modifier_symbole")
async def modifier_symbole(ctx, nom: str, nouveau_symbole: str):
    if nom not in personnages:
        await ctx.send("Personnage non trouvé.")
        return
    personnages[nom]['symbole'] = nouveau_symbole
    sauvegarder()
    await ctx.send(f"Symbole de **{nom}** modifié en **{nouveau_symbole}**.")

@bot.command(name="modifier_image")
async def modifier_image(ctx, nom: str):
    if nom not in personnages:
        await ctx.send("Personnage non trouvé.")
        return
    if not ctx.message.attachments:
        await ctx.send("Merci d'envoyer une image avec la commande.")
        return
    image = ctx.message.attachments[0]
    personnages[nom]["image_url"] = image.url
    sauvegarder()
    await ctx.send(f"Image de **{nom}** modifiée avec succès.")

@bot.command(name="modifier_permission")
async def modifier_permission(ctx, nom: str, restreint: bool):
    if nom not in personnages:
        await ctx.send("Personnage non trouvé.")
        return
    personnages[nom]["restreint"] = restreint
    if restreint:
        await ctx.send(f"Envoyez les rôles autorisés en les mentionnant (ex: @Role1 @Role2).")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await bot.wait_for('message', check=check, timeout=60)
            roles = [role.id for role in msg.role_mentions]
            personnages[nom]["roles"] = roles
        except:
            await ctx.send("Temps écoulé sans réponse. Aucun rôle défini.")
    else:
        personnages[nom]["roles"] = []

    sauvegarder()
    await ctx.send(f"Permissions de **{nom}** mises à jour.")

@bot.command(name="supprimer")
async def supprimer(ctx, nom: str):
    if nom in personnages:
        del personnages[nom]
        sauvegarder()
        await ctx.send(f"Personnage **{nom}** supprimé.")
    else:
        await ctx.send("Personnage non trouvé.")

@bot.command(name="liste")
async def liste(ctx):
    if not personnages:
        await ctx.send("Aucun personnage créé pour le moment.")
    else:
        liste_noms = "\n".join(personnages.keys())
        await ctx.send(f"Personnages existants :\n{liste_noms}")

@bot.command(name="info")
async def info(ctx, nom: str):
    if nom not in personnages:
        await ctx.send("Personnage non trouvé.")
        return
        perso = personnages[nom]
        roles = perso.get("roles", [])
        roles_mentions = ', '.join([f"<@&{r}>" for r in roles]) if roles else "Tout le monde"
        await ctx.send(f"**{nom}**\nSymbole : `{perso['symbole']}`\nType : {perso['type']}\nImage : {'Aucune' if not perso['image_url'] else perso['image_url']}\nPermissions : {roles_mentions}")

@bot.command(name="aide")
async def aide(ctx):
    await ctx.send("""
__**Commandes disponibles :**__

- `m!create <nom> <symbole> <type>` ➔ Créer un personnage
- `m!modifier_nom <ancien_nom> <nouveau_nom>` ➔ Modifier le nom d'un personnage
- `m!modifier_symbole <nom> <nouveau_symbole>` ➔ Modifier le symbole d'un personnage
- `m!modifier_image <nom>` ➔ Modifier l'image d'un personnage (avec une image jointe)
- `m!modifier_permission <nom> <True/False>` ➔ Modifier qui peut utiliser le personnage
- `m!supprimer <nom>` ➔ Supprimer un personnage
- `m!liste` ➔ Voir la liste des personnages
- `m!info <nom>` ➔ Voir les infos détaillées d'un personnage
- `m!aide` ➔ Afficher ce message
""")

# Lance le bot
bot.run(os.environ['DISCORD_TOKEN'])
