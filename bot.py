import os
import asyncio
import threading
from datetime import datetime

import discord
from discord.ext import commands
from flask import Flask, request, jsonify

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CANAL_LOG_ID = int(os.environ.get("CANAL_LOG_ID", 0))
API_SECRET = os.environ.get("API_SECRET", "secreta")
PORT = int(os.environ.get("PORT", 5000))

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


async def enviar_log(dados):
    if not canal_log:
        return

    jogador = dados.get("jogador", "Desconhecido")
    displayname = dados.get("displayname", jogador)
    userid = dados.get("userid", "")
    thumbnail = dados.get("thumbnail", "")
    mensagem = dados.get("mensagem", "")
    tipo = dados.get("tipo", "")
    link = dados.get("link", "")

    # Cor baseada no tipo
    if tipo == "entrou":
        cor = 0x57F287  # Verde
        emoji = "🟢"
    elif tipo == "saiu":
        cor = 0xED4245  # Vermelho
        emoji = "🔴"
    elif tipo == "convite":
        cor = 0x5865F2  # Azul Discord
        emoji = "📨"
    else:
        cor = 0xFEE75C  # Amarelo
        emoji = "📩"

    embed = discord.Embed(
        title=f"{emoji} {mensagem}",
        color=cor,
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="👤 Nick", value=f"{displayname} ({jogador})", inline=True)
    embed.add_field(name="🆔 UserID", value=str(userid), inline=True)

    if link:
        embed.add_field(
            name="🔗 Link do Servidor",
            value=f"[**Clique aqui para entrar**]({link})",
            inline=False
        )

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    embed.set_footer(text="Delta Executor Bot")

    await canal_log.send(embed=embed)


@app.route("/executor", methods=["POST"])
def receber():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400
    if dados.get("secret") != API_SECRET:
        return jsonify({"erro": "Não autorizado"}), 403

    if loop:
        asyncio.run_coroutine_threadsafe(enviar_log(dados), loop)

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
