import json
import logging
import os
from typing import Dict, List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# ==============================
# CONFIGURATION
# ==============================

TOKEN = "8635935168:AAHhcrHHDpkoKM0QvZAE5KXz4IfN_gNvRmM"
DATA_FILE = "lecture_data.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ==============================
# STOCKAGE
# ==============================

def load_data() -> Dict:
    if not os.path.exists(DATA_FILE):
        return {"readers": [], "listeners": []}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"readers": [], "listeners": []}


def save_data(data: Dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==============================
# NOM UTILISATEUR
# ==============================

def display_name(user) -> str:
    if user.username:
        return f"@{user.username}"

    full_name = " ".join(
        part for part in [user.first_name, user.last_name] if part
    )

    return full_name.strip() or "Sans nom"

# ==============================
# TEXTE DE LA FICHE
# ==============================

def build_text(data: Dict) -> str:
    readers: List[str] = data.get("readers", [])
    listeners: List[str] = data.get("listeners", [])

    if readers:
        readers_block = "\n".join(
            f"{i+1}. {name}" for i, name in enumerate(readers)
        )
    else:
        readers_block = "—"

    if listeners:
        listeners_block = "\n".join(
            f"• {name}" for name in listeners
        )
    else:
        listeners_block = "—"

    text = (
        "بسم الله الرحمن الرحيم\n\n"
        "📖 Académie Tawhid\n\n"
        "Lecture du jour\n\n"
        "📚 Je lis\n"
        f"{readers_block}\n\n"
        "🎧 J'écoute\n"
        f"{listeners_block}\n\n"
        "❌ Je supprime ma kounya\n"
        "—\n\n"
        "🤲 Qu'Allah 'Azza wa Jall facilite"
    )

    return text

# ==============================
# BOUTONS
# ==============================

def build_keyboard():

    keyboard = [
        [InlineKeyboardButton("📚 Je lis", callback_data="read")],
        [InlineKeyboardButton("🎧 J'écoute", callback_data="listen")],
        [InlineKeyboardButton("❌ Je supprime ma kounya", callback_data="remove")],
    ]

    return InlineKeyboardMarkup(keyboard)

# ==============================
# COMMANDES
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Bienvenue.\nTapez /lecture pour afficher la fiche."
    )


async def lecture(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = load_data()

    await update.message.reply_text(
        build_text(data),
        reply_markup=build_keyboard(),
    )


async def reset_liste(update: Update, context: ContextTypes.DEFAULT_TYPE):

    save_data({"readers": [], "listeners": []})

    data = load_data()

    await update.message.reply_text(
        "Liste réinitialisée."
    )

    await update.message.reply_text(
        build_text(data),
        reply_markup=build_keyboard(),
    )

# ==============================
# GESTION DES BOUTONS
# ==============================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    try:
        await query.answer()
    except:
        pass

    user = query.from_user
    name = display_name(user)
    action = query.data

    data = load_data()

    readers: List[str] = data.get("readers", [])
    listeners: List[str] = data.get("listeners", [])

    if action == "read":

        if name in listeners:
            listeners.remove(name)

        if name not in readers:
            readers.append(name)

    elif action == "listen":

        if name in readers:
            readers.remove(name)

        if name not in listeners:
            listeners.append(name)

    elif action == "remove":

        if name in readers:
            readers.remove(name)

        if name in listeners:
            listeners.remove(name)

    data["readers"] = readers
    data["listeners"] = listeners

    save_data(data)

    await query.edit_message_text(
        text=build_text(data),
        reply_markup=build_keyboard(),
    )

# ==============================
# LANCEMENT
# ==============================

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lecture", lecture))
    app.add_handler(CommandHandler("resetliste", reset_liste))

    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot lancé")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()