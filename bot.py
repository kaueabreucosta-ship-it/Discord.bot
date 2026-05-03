from datetime import datetime, timezone
import discord

async def enviar_log(dados):
    if not canal_log:
        print("Canal não encontrado!")
        return

    # Extrai os dados
    jogador = dados.get("jogador", "Desconhecido")
    displayname = dados.get("displayname", jogador)
    userid = dados.get("userid", "")
    thumbnail = dados.get("thumbnail", "").strip()
    mensagem = dados.get("mensagem", "")
    tipo = dados.get("tipo", "")
    link = dados.get("link", "")

    # Define cor e emoji conforme o tipo
    if tipo == "entrou":
        cor = 0x57F287
        emoji = "🟢"
    elif tipo == "saiu":
        cor = 0xED4245
        emoji = "🔴"
    elif tipo == "convite":
        cor = 0x5865F2
        emoji = "📨"
    else:
        cor = 0xFEE75C
        emoji = "📩"

    embed = discord.Embed(
        title=f"{emoji} {mensagem}",
        color=cor,
        timestamp=datetime.now(timezone.utc)
    )

    embed.add_field(name="👤 Nick", value=f"{displayname} ({jogador})", inline=True)
    embed.add_field(name="🆔 UserID", value=str(userid), inline=True)

    if link:
        embed.add_field(
            name="🔗 Link do Servidor",
            value=f"[**Clique aqui para entrar**]({link})",
            inline=False
        )

    # ====================== THUMBNAIL MELHORADA ======================
    if thumbnail and thumbnail.startswith(("http://", "https://")):
        # Verifica se tem extensão válida de imagem
        extensoes_validas = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
        
        url_limpa = thumbnail.split('?')[0]  # remove query string
        
        if any(url_limpa.lower().endswith(ext) for ext in extensoes_validas):
            try:
                embed.set_thumbnail(url=thumbnail)
                print(f"✅ Thumbnail aplicada: {thumbnail[:80]}...")
            except Exception as e:
                print(f"❌ Erro ao aplicar thumbnail: {e}")
        else:
            print(f"⚠️ Thumbnail rejeitada (sem extensão válida): {thumbnail[:100]}...")
    else:
        print("⚠️ Nenhuma thumbnail válida enviada.")
    # ================================================================

    embed.set_footer(text="Delta Executor Bot")

    try:
        await canal_log.send(embed=embed)
        print(f"✅ Embed enviado com sucesso - Tipo: {tipo}")
    except Exception as e:
        print(f"❌ Erro ao enviar embed: {e}")
