import discord
from discord.ext import commands
import random
import json
import os
import asyncio

# --- Keep Alive Server pour héberger ton bot ---

import threading
import http.server
import socketserver

# Choisis ton port (tu peux laisser 8080)
PORT = 8080

# Handler pour répondre à toutes les requêtes entrantes
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)  # OK
        self.send_header('Content-type', 'text/html')  # Type de la réponse
        self.end_headers()
        self.wfile.write("🚀 Bot RP Manager est en ligne !".encode('utf-8'))

# Fonction pour lancer le serveur
def run_web():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🛰️ Serveur keep_alive actif sur le port {PORT}")
        httpd.serve_forever()

# Fonction keep_alive() à appeler au lancement du bot
def keep_alive():
    thread = threading.Thread(target=run_web)
    thread.start()

# Charger les personnages
if not os.path.exists('data.json'):
    with open('data.json', 'w') as f:
        json.dump({}, f)

with open('data.json', 'r') as f:
    personnages = json.load(f)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="m!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} est connecté avec succès !")

# -------------------------------
# COMMANDES
# -------------------------------

@bot.command(name="creer_personnage")
async def creer_personnage(ctx, nom: str, symbole: str):
    if nom in personnages:
        await ctx.send(f"❌ Le personnage **{nom}** existe déjà !")
        return

    # Récupérer l'image envoyée avec le message
    image_url = None
    if ctx.message.attachments:
        image_url = ctx.message.attachments[0].url

    personnages[nom] = {
        "symbole": symbole,
        "type": "Inconnu",  # Type par défaut
        "image_url": image_url,
        "banniere_url": None,
        "restreint": False,
        "roles_autorises": [],
        "role_associe": None,
        "pouvoir": None,
        "couleur": "bleu",
        "histoire": None,
        "position": {"x": 0, "y": 0},
        "relations": {
            "Amis": [],
            "Ennemis": [],
            "Famille": []
        }
    }

    await ctx.send(f"✅ Personnage **{nom}** créé avec succès !")

    
@bot.command(name="banniere")
async def modifier_banniere(ctx, nom: str):
    if nom not in personnages:
        await ctx.send(f"❌ Le personnage {nom} n'existe pas.")
        return

    if not ctx.message.attachments:
        await ctx.send("❌ Merci d'envoyer une image en pièce jointe avec la commande.")
        return

    attachment = ctx.message.attachments[0]
    personnages[nom]['banniere_url'] = attachment.url

    with open('data.json', 'w') as f:
        json.dump(personnages, f, indent=4)

    await ctx.send(f"✅ La bannière du personnage {nom} a été mise à jour avec succès !")

@bot.command()
async def definir_type(ctx, nom: str, type_perso: str):
    if nom not in personnages:
        await ctx.send(f"❌ Le personnage {nom} n'existe pas.")
        return

    personnages[nom]["type"] = type_perso
    with open('data.json', 'w') as f:
        json.dump(personnages, f, indent=4)
    await ctx.send(f"✅ Type de {nom} mis à jour ({type_perso}) !")

@bot.command()
async def modifier_nom(ctx, nom: str, nouveau_nom: str):
    if nom not in personnages:
        await ctx.send(f"❌ Le personnage {nom} n'existe pas.")
        return

    personnages[nouveau_nom] = personnages.pop(nom)
    with open('data.json', 'w') as f:
        json.dump(personnages, f, indent=4)
    await ctx.send(f"✅ Nom modifié : {nom} ➔ {nouveau_nom}")

@bot.command()
async def modifier_image(ctx, nom: str):
    if nom not in personnages:
        await ctx.send(f"❌ Ce personnage n'existe pas.")
        return
    if not ctx.message.attachments:
        await ctx.send(f"❌ Tu dois envoyer une image en pièce jointe.")
        return

    personnages[nom]["image_url"] = ctx.message.attachments[0].url
    with open('data.json', 'w') as f:
        json.dump(personnages, f, indent=4)
    await ctx.send(f"🖼️ Image de {nom} mise à jour !")

@bot.command()
async def sup_perso(ctx, nom: str):
    if nom not in personnages:
        await ctx.send(f"❌ Personnage {nom} introuvable.")
        return
    personnages.pop(nom)
    with open('data.json', 'w') as f:
        json.dump(personnages, f, indent=4)
    await ctx.send(f"🗑️ Personnage {nom} supprimé.")

@bot.command()
async def changer_symbole(ctx, nom: str, nouveau_symbole: str):
    if nom not in personnages:
        await ctx.send(f"❌ Personnage introuvable.")
        return
    personnages[nom]["symbole"] = nouveau_symbole
    with open('data.json', 'w') as f:
        json.dump(personnages, f, indent=4)
    await ctx.send(f"🔄 Symbole de {nom} changé.")

@bot.command(name="info_perso")
async def info_perso(ctx, nom: str):
    if nom not in personnages:
        await ctx.send(f"❌ Le personnage {nom} n'existe pas.")
        return

    infos = personnages[nom]
    desc = f"**{nom}**\n"
    desc += f"Symbole : `{infos['symbole']}`\n"
    desc += f"Type : {infos.get('type', 'Inconnu')}\n"
    desc += f"Pouvoir : {infos.get('pouvoir', 'Non défini')}\n"

    # Rôles autorisés
    roles = infos.get("roles_autorises", [])
    if roles:
        roles_mentions = [f"<@&{role_id}>" for role_id in roles]
        desc += f"🔒 Rôles autorisés : {', '.join(roles_mentions)}\n"
    else:
        desc += "🔓 Rôles autorisés : Tout le monde\n"

    # Rôle associé
    role_associe = infos.get("role_associe")
    if role_associe:
        desc += f"🎭 Rôle associé : <@&{role_associe}>\n"
    else:
        desc += "🎭 Rôle associé : Aucun\n"

    ## Couleur personnalisée avec code hexadécimal
    couleur_code = infos.get("couleur", "#3498db")  # bleu par défaut

    try:
        couleur_embed = discord.Color(int(couleur_code[1:], 16))
    except ValueError:
        couleur_embed = discord.Color.blue()

    embed = discord.Embed(
        title=f"📜 Fiche de {nom}",
        description=desc,
        color=couleur_embed
        )

    image_url = infos.get("image_url")
    if image_url:
        embed.set_thumbnail(url=image_url)  # PETITE IMAGE en haut à droite

    banniere_url = infos.get("banniere_url")
    if banniere_url:
        embed.set_image(url=banniere_url)  # GRANDE BANNIÈRE en bas

    await ctx.send(embed=embed)



@bot.command()
async def pouvoir(ctx, nom: str, *, pouvoir_texte: str):
    if nom not in personnages:
        await ctx.send(f"❌ Le personnage {nom} n'existe pas.")
        return

    personnages[nom]["pouvoir"] = pouvoir_texte
    with open('data.json', 'w') as f:
        json.dump(personnages, f, indent=4)
    await ctx.send(f"✨ Pouvoir de {nom} mis à jour : {pouvoir_texte}")

@bot.command(name="role")
async def role(ctx, nom: str, role: discord.Role):
    if nom not in personnages:
        await ctx.send(f"❌ Le personnage **{nom}** n'existe pas.")
        return

    personnages[nom]["role_associe"] = role.id

    with open('data.json', 'w') as f:
        json.dump(personnages, f, indent=4)

    await ctx.send(f"🎭 Le rôle **{role.name}** a été associé au personnage **{nom}** !")

@bot.command(name="restreins")
async def restreins(ctx, nom: str, role: discord.Role):
    if nom not in personnages:
        await ctx.send(f"❌ Le personnage **{nom}** n'existe pas.")
        return

    # Si le perso n'a pas encore de liste de rôles restreints
    if "roles_autorises" not in personnages[nom]:
        personnages[nom]["roles_autorises"] = []

    if role.id not in personnages[nom]["roles_autorises"]:
        personnages[nom]["roles_autorises"].append(role.id)

    with open('data.json', 'w') as f:
        json.dump(personnages, f, indent=4)

    await ctx.send(f"🔒 Le personnage **{nom}** est maintenant restreint au rôle **{role.name}** !")

@bot.command(name="role_retirer")
async def role_retirer(ctx, nom: str, role: discord.Role):
    if nom not in personnages:
        await ctx.send(f"❌ Le personnage **{nom}** n'existe pas.")
        return

    if personnages[nom].get("role_associe") != role.id:
        await ctx.send(f"❌ Le rôle {role.name} n'est pas associé à **{nom}**.")
        return

    personnages[nom]["role_associe"] = None

    with open('data.json', 'w') as f:
        json.dump(personnages, f, indent=4)

    await ctx.send(f"🎭 Le rôle **{role.name}** a été retiré du personnage **{nom}** !")

@bot.command(name="restreins_retirer")
async def restreins_retirer(ctx, nom: str, role: discord.Role):
    if nom not in personnages:
        await ctx.send(f"❌ Le personnage **{nom}** n'existe pas.")
        return

    if "roles_autorises" not in personnages[nom] or role.id not in personnages[nom]["roles_autorises"]:
        await ctx.send(f"❌ Le rôle {role.name} n'était pas restreint pour **{nom}**.")
        return

    personnages[nom]["roles_autorises"].remove(role.id)

    # Si plus aucun rôle autorisé, on supprime complètement la restriction
    if not personnages[nom]["roles_autorises"]:
        del personnages[nom]["roles_autorises"]

    with open('data.json', 'w') as f:
        json.dump(personnages, f, indent=4)

    await ctx.send(f"🔓 Le rôle **{role.name}** a été retiré des restrictions pour **{nom}** !")

@bot.command(name="couleur_fiche")
async def couleur_fiche(ctx, nom: str, couleur: str):
    if nom not in personnages:
        await ctx.send(f"❌ Le personnage {nom} n'existe pas.")
        return

    if not couleur.startswith("#") or len(couleur) != 7:
        await ctx.send("❌ Couleur invalide. Utilise un code hexadécimal comme `#FF0000`.")
        return

    try:
        int(couleur[1:], 16)  # vérifier si c'est bien un code hexadécimal
    except ValueError:
        await ctx.send("❌ Ce n'est pas un vrai code couleur.")
        return

    personnages[nom]["couleur"] = couleur
    with open('data.json', 'w') as f:
        json.dump(personnages, f, indent=4)

    await ctx.send(f"✅ Couleur de la fiche de {nom} changée en {couleur} !")

@bot.command(name="histoire")
async def histoire(ctx, nom: str, *, texte: str = None):
    if nom not in personnages:
        await ctx.send(f"❌ Le personnage {nom} n'existe pas.")
        return

    if texte is None:
        histoire = personnages[nom].get("histoire")
        if histoire:
            await ctx.send(f"📖 Histoire de **{nom}**:\n\n{histoire}")
        else:
            await ctx.send(f"❌ {nom} n'a pas encore d'histoire.")
    else:
        personnages[nom]["histoire"] = texte
        with open('data.json', 'w') as f:
            json.dump(personnages, f, indent=4)
        await ctx.send(f"✅ Histoire de {nom} mise à jour !")

@bot.command(name="carte")
async def carte(ctx):
    largeur, hauteur = 20, 10  # Taille de la carte
    grille = [["." for _ in range(largeur)] for _ in range(hauteur)]

    # Placer les personnages
    for nom, infos in personnages.items():
        pos = infos.get("position", {"x": 0, "y": 0})
        x, y = pos.get("x", 0), pos.get("y", 0)
        if 0 <= x < largeur and 0 <= y < hauteur:
            symbole = infos.get("symbole", "?")
            grille[y][x] = symbole

    # Dessiner la carte
    texte = "🗺️ **Carte du Monde**\n\n"
    for ligne in grille:
        texte += " ".join(ligne) + "\n"

    await ctx.send(texte)

@bot.command(name="combat_perso")
async def combat_perso_vs_perso(ctx, perso1: str, vs: str, perso2: str):
    if nom not in personnages:
        await ctx.send(f"❌ Le personnage {nom} n'existe pas.")
        return

    largeur, hauteur = 20, 10
    if not (0 <= x < largeur) or not (0 <= y < hauteur):
        await ctx.send(f"❌ Coordonnées invalides ! (x doit être entre 0 et {largeur-1}, y entre 0 et {hauteur-1})")
        return

    personnages[nom]["position"] = {"x": x, "y": y}
    await ctx.send(f"✅ {nom} a été déplacé en position ({x}, {y}) !")

@bot.command(name="relation")
async def relation(ctx, nom: str):
    if nom not in personnages:
        await ctx.send(f"❌ Le personnage {nom} n'existe pas.")
        return

    relations = personnages[nom].get("relations", {})

    amis = relations.get("Amis", [])
    ennemis = relations.get("Ennemis", [])
    famille = relations.get("Famille", [])

    texte = f"**📜 Relations de {nom} :**\n\n"
    texte += f"👥 **Amis** : {', '.join(amis) if amis else 'Aucun'}\n"
    texte += f"⚔️ **Ennemis** : {', '.join(ennemis) if ennemis else 'Aucun'}\n"
    texte += f"👨‍👩‍👧‍👦 **Famille** : {', '.join(famille) if famille else 'Aucun'}"

    await ctx.send(texte)

@bot.command(name="relation_modifier")
async def relation_modifier(ctx, nom: str, type_relation: str, cible: discord.Member):
    if nom not in personnages:
        await ctx.send(f"❌ Le personnage {nom} n'existe pas.")
        return

    type_relation = type_relation.capitalize()
    if type_relation not in ["Amis", "Ennemis", "Famille"]:
        await ctx.send("❌ Type de relation invalide. Utilise `Amis`, `Ennemis` ou `Famille`.")
        return

    relations = personnages[nom].setdefault("relations", {
        "Amis": [],
        "Ennemis": [],
        "Famille": []
    })

    cible_nom = cible.display_name

    # Ajout ou suppression
    if cible_nom in relations[type_relation]:
        relations[type_relation].remove(cible_nom)
        action = "❌ Retiré de"
    else:
        relations[type_relation].append(cible_nom)
        action = "✅ Ajouté à"

    # Sauvegarder
    with open('data.json', 'w') as f:
        json.dump(personnages, f, indent=4)

    await ctx.send(f"{action} **{type_relation}** de **{nom}** : {cible_nom}")

# Chargement des données
if os.path.exists("data.json"):
    with open("data.json", "r") as f:
        players = json.load(f)
else:
    players = {}

def save_data():
    with open("data.json", "w") as f:
        json.dump(players, f, indent=4)

# Config niveaux/récompenses
level_up_requirements = {
    2: 100,
    5: 500,
    10: 1200,
    20: 3000,
}

role_rewards = {
    5: "Guerrier",
    10: "Champion",
    20: "Légende",
}

equipment_rewards = {
    2: "Casque en cuir",
    5: "Épée en fer",
    10: "Armure d'or",
    20: "Épée légendaire",
}

# Ajouter de l'XP
async def add_xp(member, amount):
    user_id = str(member.id)
    if user_id not in players:
        players[user_id] = {"xp": 0, "level": 1, "inventory": []}

    players[user_id]["xp"] += amount
    xp = players[user_id]["xp"]
    level = players[user_id]["level"]

    for lvl, required_xp in sorted(level_up_requirements.items()):
        if xp >= required_xp and lvl > level:
            players[user_id]["level"] = lvl
            await reward_player(member, lvl)

    save_data()

# Récompense automatique
async def reward_player(member, level):
    guild = member.guild
    user_id = str(member.id)

    if level in role_rewards:
        role_name = role_rewards[level]
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            await member.add_roles(role)

    if level in equipment_rewards:
        item = equipment_rewards[level]
        players[user_id]["inventory"].append(item)

    await member.send(f"🎉 Bravo {member.name}, tu es monté au niveau {level} !")

# Ajouter XP sur chaque message/commande
@bot.event
async def on_command(ctx):
    await add_xp(ctx.author, 10)  # 10 XP par commande

# ------------------ COMMANDES ------------------

@bot.command()
async def xp(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    user_id = str(member.id)
    xp = players.get(user_id, {}).get("xp", 0)
    await ctx.send(f"🔵 {member.display_name} a {xp} XP.")

@bot.command()
async def niveau(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    user_id = str(member.id)
    level = players.get(user_id, {}).get("level", 1)
    await ctx.send(f"🟣 {member.display_name} est niveau {level}.")

@bot.command()
async def grades(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    user_id = str(member.id)
    level = players.get(user_id, {}).get("level", 1)

    current_grade = "Aucun"
    for lvl, grade in sorted(role_rewards.items(), reverse=True):
        if level >= lvl:
            current_grade = grade
            break

    await ctx.send(f"🛡️ {member.display_name} a pour grade : {current_grade}")

@bot.command()
async def equipement(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    user_id = str(member.id)
    inventory = players.get(user_id, {}).get("inventory", [])
    if inventory:
        items = "\n".join(f"🛡️ {item}" for item in inventory)
        await ctx.send(f"🎒 Équipements de {member.display_name} :\n{items}")
    else:
        await ctx.send(f"🎒 {member.display_name} n'a pas encore d'équipement.")

import json
import os

@bot.command(name="topxp_serveur")
async def topxp_serveur(ctx):
    if os.path.exists("xp_data.json"):
        with open("xp_data.json", "r") as f:
            xp_data = json.load(f)
    else:
        await ctx.send("⚠️ Pas encore de données d'XP.")
        return

    membres = [(int(user_id), data["xp"]) for user_id, data in xp_data.items()]
    membres.sort(key=lambda x: x[1], reverse=True)

    top10 = membres[:10]

    message = "**🏆 Top 10 XP du serveur :**\n"
    for i, (user_id, xp) in enumerate(top10, 1):
        membre = ctx.guild.get_member(user_id)
        if membre:
            message += f"{i}. {membre.display_name} - {xp} XP\n"

    await ctx.send(message)

@bot.command(name="topxp")
async def topxp(ctx):
    if os.path.exists("xp_data.json"):
        with open("xp_data.json", "r") as f:
            xp_data = json.load(f)
    else:
        await ctx.send("⚠️ Pas encore de données d'XP.")
        return

    membres = [(user_id, data["xp"]) for user_id, data in xp_data.items()]
    membres.sort(key=lambda x: x[1], reverse=True)

    top10 = membres[:10]

    message = "**🌍 Top 10 XP Global :**\n"
    for i, (user_id, xp) in enumerate(top10, 1):
        utilisateur = await bot.fetch_user(int(user_id))
        message += f"{i}. {utilisateur.name} - {xp} XP\n"

    await ctx.send(message)

@bot.command(name="profil_histoire")
async def profil_histoire(ctx, *, histoire):
    profils = get_profil(ctx.author)
    profils[str(ctx.author.id)]["histoire"] = histoire

    with open("profils.json", "w") as f:
        json.dump(profils, f, indent=4)

    await ctx.send("✅ Ton histoire a été mise à jour !")

@bot.command(name="profil_couleur")
async def profil_couleur(ctx, couleur):
    if not couleur.startswith("#") or len(couleur) != 7:
        await ctx.send("❌ Format incorrect ! Exemple : `#ff0000`")
        return

    profils = get_profil(ctx.author)
    profils[str(ctx.author.id)]["couleur"] = couleur

    with open("profils.json", "w") as f:
        json.dump(profils, f, indent=4)

    await ctx.send("✅ Ta couleur de profil a été mise à jour !")

@bot.command(name="profil_type")
async def profil_type(ctx, *, type_personnalise):
    profils = get_profil(ctx.author)
    profils[str(ctx.author.id)]["type"] = type_personnalise

    with open("profils.json", "w") as f:
        json.dump(profils, f, indent=4)

    await ctx.send("✅ Ton type a été mis à jour !")

@bot.command(name="profil_pouvoir")
async def profil_pouvoir(ctx, *, pouvoir):
    profils = get_profil(ctx.author)
    profils[str(ctx.author.id)]["pouvoir"] = pouvoir

    with open("profils.json", "w") as f:
        json.dump(profils, f, indent=4)

    await ctx.send("✅ Ton pouvoir a été mis à jour !")

@bot.command(name="profil")
async def profil(ctx, membre: discord.Member = None):
    if membre is None:
        membre = ctx.author

    profils = get_profil(membre)
    infos = profils.get(str(membre.id), None)

    if infos is None:
        await ctx.send("❌ Ce membre n'a pas encore personnalisé son profil.")
        return

    embed = discord.Embed(
        title=f"Profil de {membre.display_name}",
        description=f"**Type :** {infos['type']}\n"
                    f"**Pouvoir :** {infos['pouvoir']}\n\n"
                    f"**Histoire :**\n{infos['histoire']}",
        color=int(infos["couleur"].lstrip('#'), 16)
    )
    embed.set_thumbnail(url=membre.avatar.url)

    await ctx.send(embed=embed)

@bot.command()
async def aide(ctx):
    commandes = """
**Commandes disponibles :**
Cretion personnages et gestion :
📄 m!creer_personnage <nom> <symbole> ➔ Créer un personnage
🔧 m!definir_type <nom> <type> ➔ Définir le type du personnage
✏️ m!modifier_nom <nom> <nouveau_nom> ➔ Modifier le nom
🗑️ m!sup_perso <nom> ➔ Supprimer un personnage
🔣 m!changer_symbole <nom> <symbole> ➔ Changer le symbole

Affichage :
⚙️ m!liste_personnage ➔ Voir la liste des personnages
⚙️ m!aide ➔ Voir les commandes disponibles

Personalisation des personnages :
🖼️ m!modifier_image <nom> ➔ Modifier l'image
🏞️ m!banniere <nom> ➔ Modifier la bannière
🧾 m!info_perso <nom> ➔ Voir la description
✨ m!pouvoir <nom> <pouvoir> ➔ Définir un pouvoir
🎭 m!role <nom> <rôle> ➔ Associer un rôle serveur
❌ m!role_retirer <nom> <role> ➔ Retirer le role d'un personnage
🎨 m!couleur_fiche <nom> <couleur> ➔ Change la couleur de la fiche du personnage
🔒 m!restreins <nom> <role> ➔ Restreindre l'utilisation du personnage à un rôle
🔓 m!restreins_retirer <nom> <role> ➔ Retirer la restriction

Histoire des personnages :
📖 m!histoire <nom> ➔ Voir ou définir l'histoire du personnage
📖 m!histoire <nom> <histoire>... ➔ Change ou ajoute l’histoire.
👥 m!relation <nom> → pour afficher ses amis, ennemis, famille.
👥 m!relation_modifier <nom> <Amis/Ennemis/Famille> <@mention>  → pour ajouter/supprimer des relations.

Profil utilisateur :
m!profil_histoire ➔Personnaliser l'histoire de son personnage
m!profil_couleur ➔ Modifier la couleur de son profil
m!profil_type ➔ Choisir le type/race de son personnage
m!profil_pouvoir ➔ Définir son pouvoir magique/spécial
m!profil ➔ Voir son propre profil ou celui d'un membre

Carte :
🗺️ m!catre ➔ Affiche la carte du monde
🗺️ m!carte_control <nom> <x> <y> ➔ Déplacer un personnage sur la carte

Niveau :
🏅 m!xp <@membre> → Affiche le nombre d'XP du membre (ou toi-même si vide)
🏅 m!niveau <@membre> → Affiche ton niveau actuel
🏅 m!grades <@membre> → Affiche ton grade en fonction de ton niveau
🏅 m!equipement <@membre> → Affiche ton inventaire d’équipements gagnés avec le niveau

Top XP :
m!topxp_serveur → Top 10 membres avec le plus d'XP du serveur
m!topxp → Top 10 membres global (tous les utilisateurs du bot)

Bonus :
😂 m!blague ➔ Blague aléatoire
🌟 m!inspire ➔ Citation inspirante
🔮 m!fortune ➔ Prédiction mystique
🐾 m!animal ➔ Animal totem
🎨 m!couleur ➔ Couleur mystique

    """

    # Si le texte dépasse 2000 caractères, on le coupe en morceaux
    for i in range(0, len(commandes), 2000):
        await ctx.send(commandes[i:i+2000])


# Fun Commands
@bot.command()
async def blague(ctx):
    blagues = [
        "Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant ? Parce que sinon ils tombent dans le bateau.",
        "Que dit une maman tomate à son bébé tomate qui traîne ? Ketchup !",
        "Pourquoi les vampires n'aiment-ils pas les pizzas ? Parce qu'ils détestent l'ail."
    ]
    await ctx.send(random.choice(blagues))

@bot.command()
async def inspire(ctx):
    citations = [
        "Crois en toi et en tes rêves. ✨",
        "La persévérance est la clé du succès.",
        "Chaque jour est une nouvelle chance de briller."
    ]
    await ctx.send(random.choice(citations))

@bot.command()
async def fortune(ctx):
    predictions = [
        "Une grande aventure t'attend !",
        "Aujourd'hui est ton jour de chance.",
        "Attention aux décisions impulsives."
    ]
    await ctx.send(random.choice(predictions))

@bot.command()
async def animal(ctx):
    animaux = ["Loup", "Aigle", "Tigre", "Licorne", "Phénix"]
    await ctx.send(f"Ton animal totem est : **{random.choice(animaux)}** !")

@bot.command()
async def couleur(ctx):
    couleurs = ["Rouge passion", "Bleu céleste", "Vert émeraude", "Noir mystère", "Doré royal"]
    await ctx.send(f"Ta couleur mystique est : **{random.choice(couleurs)}** !")

# -------------------------------
# SYMBOLE POUR FAIRE PARLER LE PERSONNAGE
# -------------------------------

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    for nom, infos in personnages.items():
        symbole = infos["symbole"]

        if message.content.startswith(symbole):
            if infos["roles_autorises"]:
                if not any(role.id in infos["roles_autorises"] for role in message.author.roles):
                    await message.channel.send("❌ Tu n'as pas la permission d'utiliser ce personnage.", delete_after=5)
                    return

            texte = message.content[len(symbole):].strip()

            webhook = await message.channel.create_webhook(name=nom)
            await webhook.send(
                texte,
                username=nom,
                avatar_url=infos["image_url"] if infos["image_url"] else bot.user.avatar.url
            )
            await webhook.delete()
            await message.delete()
            break

    await bot.process_commands(message)

# -------------------------------
# LANCEMENT DU BOT
# -------------------------------
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
