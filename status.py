import discord
import asyncio
from mcstatus import JavaServer, BedrockServer

# 從 TOKEN.txt 讀取 Token
def get_token():
    with open("TOKEN.txt", "r", encoding="utf-8") as file:
        return file.read().strip()  # 讀取並移除空白與換行符號

TOKEN = get_token()

# 伺服器 IP 和端口
JAVA_SERVER = "ouo.freeserver.tw"
JAVA_PORT = 24030

BEDROCK_SERVER = "ouo.freeserver.tw"
BEDROCK_PORT = 24030  # Bedrock 版使用相同端口

# 伺服器官網 IP（新增）
SERVER_WEBSITE = "https://whitecloud.us.kg"

# 設定 Discord 頻道 ID
CHANNEL_ID = 1335773767900594268  # 請填入你的 Discord 頻道 ID

# 設定 Bot 權限
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"已登入為 {client.user}")
    await send_status_loop()

async def send_status_loop():
    """每 40 秒更新一次伺服器狀態到指定頻道"""
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        print("找不到指定的頻道，請確認 CHANNEL_ID 是否正確")
        return

    message = None
    while not client.is_closed():
        # 取得伺服器狀態
        try:
            java_status = JavaServer.lookup(f"{JAVA_SERVER}:{JAVA_PORT}").status()
            java_online = java_status.players.online
            java_max = java_status.players.max
            java_latency = int(java_status.latency)  # 把延遲轉換為整數
        except Exception:
            java_online, java_max, java_latency = 0, "?", "無法連線"

        try:
            bedrock_status = BedrockServer.lookup(f"{BEDROCK_SERVER}:{BEDROCK_PORT}").status()
            bedrock_online = bedrock_status.players_online
            bedrock_max = bedrock_status.players_max
            bedrock_latency = int(bedrock_status.latency)  # 把延遲轉換為整數
        except Exception:
            bedrock_online, bedrock_max, bedrock_latency = 0, "?", "無法連線"

        total_players = java_online + bedrock_online
        countdown = 40

        # 更新訊息
        while countdown > 0:
            embed = discord.Embed(title="Minecraft 伺服器狀態", color=0x00ff00)
            embed.add_field(name="Java 版", value=f"玩家: {java_online}/{java_max}\n延遲: {java_latency} ms", inline=False)
            embed.add_field(name="Bedrock 版", value=f"玩家: {bedrock_online}/{bedrock_max}\n延遲: {bedrock_latency} ms", inline=False)
            embed.add_field(name="總在線玩家", value=f"{total_players} 位玩家在線", inline=False)
            embed.add_field(name="伺服器官網", value=f"[點擊這裡查看](https://whitecloud.us.kg)", inline=False)
            embed.set_footer(text=f"下次刷新: {countdown} 秒後")

            if message is None:
                message = await channel.send(embed=embed)
            else:
                await message.edit(embed=embed)

            countdown -= 1
            await asyncio.sleep(1)

client.run(TOKEN)