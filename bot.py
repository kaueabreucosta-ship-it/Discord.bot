import os
import asyncio
import threading
from datetime import datetime

import discord
from discord.ext import commands
from flask import Flask, request, jsonify

# Configurações via variáveis de ambiente (Railway)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CANAL_LOG_ID = int(os.environ.get("CANAL_LOG_ID", 0))
API_SECRET = os.environ.get("API_SECRET", "secreta")
PORT = int(os.environ.get("PORT", 5000))

# Setup do bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
app = Flask(__name__)

canal_log = None
loop = None


@bot.event
async def on_ready():
    global canal_log
    canal_log = bot.get_channel(CANAL_LOG_ID)
    print(f"Bot online: {bot.user}")


@bot.command()
async def status(ctx):
    await ctx.send("✅ Bot online e funcionando!")


async def enviar_log(jogador, mensagem):
    if canal_log:
        embed = discord.Embed(
            title="📨 Delta Executor",
            color=0x5865F2,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="👤 Jogador", value=jogador, inline=True)
        embed.add_field(name="💬 Mensagem", value=mensagem, inline=False)
        await canal_log.send(embed=embed)


@app.route("/executor", methods=["POST"])
def receber():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400
    if dados.get("secret") != API_SECRET:
        return jsonify({"erro": "Não autorizado"}), 403

    jogador = dados.get("jogador", "Desconhecido")
    mensagem = dados.get("mensagem", "")

    if loop:
        asyncio.run_coroutine_threadsafe(enviar_log(jogador, mensagem), loop)

    return jsonify({"status": "ok"}), 200


@app.route("/ping")
def ping():
    return jsonify({"status": "online"}), 200


def rodar_flask():
    app.run(host="0.0.0.0", port=PORT)


async def main():
    global loop
    loop = asyncio.get_event_loop()
    t = threading.Thread(target=rodar_flask, daemon=True)
    t.start()
    await bot.start(BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
    
