import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
from datetime import datetime

import os

# ============================================================
# CONFIGURAÇÕES — lidas das variáveis de ambiente do Railway
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CANAL_LOG_ID = int(os.environ.get("CANAL_LOG_ID", 0))
API_SECRET = os.environ.get("API_SECRET", "minha_senha_secreta")
API_PORT = int(os.environ.get("PORT", 5000))
# ============================================================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
app = Flask(__name__)

canal_log = None  # Referência ao canal, preenchida ao ligar o bot


# ------------------------------------------------------------------
# API local — recebe requests do Delta Executor
# ------------------------------------------------------------------
@app.route("/executor", methods=["POST"])
def receber_do_executor():
    """
    Endpoint chamado pelo script Lua no Delta Executor.
    Espera JSON: { "secret": "...", "mensagem": "...", "jogador": "..." }
    """
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    if dados.get("secret") != API_SECRET:
        return jsonify({"erro": "Não autorizado"}), 403

    mensagem = dados.get("mensagem", "(sem mensagem)")
    jogador = dados.get("jogador", "Desconhecido")

    # Envia para o Discord de forma thread-safe
    if canal_log:
        import asyncio
        future = asyncio.run_coroutine_threadsafe(
            enviar_log(jogador, mensagem),
            bot.loop
        )
        future.result(timeout=10)

    return jsonify({"status": "ok"}), 200


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "online"}), 200


# ------------------------------------------------------------------
# Funções do bot
# ------------------------------------------------------------------
async def enviar_log(jogador: str, mensagem: str):
    if canal_log is None:
        return

    embed = discord.Embed(
        title="📨 Mensagem do Delta Executor",
        color=0x5865F2,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="👤 Jogador", value=jogador, inline=True)
    embed.add_field(name="💬 Mensagem", value=mensagem, inline=False)
    embed.set_footer(text="Delta Executor Bot")

    await canal_log.send(embed=embed)


@bot.event
async def on_ready():
    global canal_log
    canal_log = bot.get_channel(CANAL_LOG_ID)

    if canal_log:
        print(f"✅ Bot conectado como {bot.user}")
        print(f"📢 Logs serão enviados para: #{canal_log.name}")
    else:
        print("⚠️  Canal de log não encontrado! Verifique CANAL_LOG_ID.")

    print(f"🌐 API rodando em http://localhost:{API_PORT}/executor")


@bot.command(name="status")
async def status(ctx):
    """Mostra se o bot e a API estão online."""
    embed = discord.Embed(title="✅ Status do Bot", color=0x00FF00)
    embed.add_field(name="Bot", value="Online", inline=True)
    embed.add_field(name="API", value=f"Porta {API_PORT}", inline=True)
    embed.add_field(name="Canal de Log", value=canal_log.mention if canal_log else "❌ Não configurado", inline=False)
    await ctx.send(embed=embed)


# ------------------------------------------------------------------
# Inicialização
# ------------------------------------------------------------------
def rodar_api():
    app.run(host="0.0.0.0", port=API_PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    # Roda a API Flask em uma thread separada
    t = threading.Thread(target=rodar_api, daemon=True)
    t.start()

    # Roda o bot Discord
    bot.run(BOT_TOKEN)
    
