import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import asyncio
import threading
import os
from datetime import datetime, timezone

# ===================== CONFIG =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CANAL_LOG_ID = int(os.getenv("CANAL_LOG_ID"))
API_SECRET = os.getenv("API_SECRET")

app = Flask(__name__)
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
canal_log = None

# ===================== FLASK =====================
@app.route('/log', methods=['POST'])
def receber_log():
    try:
        dados = request.json
        if not dados:
            return jsonify({"status": "erro", "message": "Sem dados"}), 400

        # Verificação simples de segurança
        if API_SECRET and dados.get("secret") != API_SECRET:
            return jsonify({"status": "não autorizado"}), 401

        # Envia o log de forma assíncrona
        asyncio.run_coroutine_threadsafe(enviar_log(dados), bot.loop)
        return jsonify({"status": "sucesso"}), 200

    except Exception as e:
        print(f"Erro na rota /log: {e}")
        return jsonify({"status": "erro"}), 500

# ===================== FUNÇÃO DO EMBED =====================
async def enviar_log(dados):
    global canal_log
    if not canal_log:
        print("Canal não configurado!")
        return

    # (Cole aqui a função enviar_log que eu te passei na mensagem anterior)

# ===================== INICIALIZAÇÃO =====================
@bot.event
async def on_ready():
    global canal_log
    canal_log = bot.get_channel(CANAL_LOG_ID)
    print(f"✅ Bot online como {bot.user}")
    print(f"📌 Canal de log configurado: {canal_log}")

# ===================== RODAR TUDO =====================
def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Inicia o Flask em uma thread separada
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Inicia o Discord Bot
    bot.run(BOT_TOKEN)
