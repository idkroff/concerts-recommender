from app.tg_client.tg_client import TelegramClient

if __name__ == "__main__":
    client = TelegramClient()
    client.serve()
