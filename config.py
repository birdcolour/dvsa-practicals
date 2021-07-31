# Telegram Setup
ENABLE_TELEGRAM = True
# Example "18299471:AAF0MlXjWgvNSQKjE48qd98J9LQI0Ekk" (Make sure to not include 'bot')
TELEGRAM_BOT_TOKEN = "telegrambottoken"
TELEGRAM_CHAT_ID = "telegramchatID"  # Example "-59977119"
# More instructions on telegram bots here - https://core.telegram.org/bots

# SMTP SETUP
ENABLE_EMAIL = False
smtp = {
    "sender": "test-availability@example.com",  # SMTP sender address
    "sender_title": "DVSA Test Check",  # SMTP sender name
    "recipient": "recipient@example.com",  # Notification recipient
    "server": "smtp.example.com",  # SMTP server address
    "login": "server-admin@example.com",  # SMTP server login
    "password": "password"  # SMTP server password
}
