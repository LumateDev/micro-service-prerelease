import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@example.com"
SMTP_PASSWORD = "your_password"

TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"

def send_email_notification(subject: str, message: str, to_email: str):
    """
    Отправляет уведомление по электронной почте.

    :param subject: Тема письма.
    :param message: Текст письма.
    :param to_email: Адрес получателя.
    """
    try:
        # Создаём сообщение
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = to_email
        msg["Subject"] = subject

        # Добавляем текст письма
        msg.attach(MIMEText(message, "plain"))

        # Подключаемся к SMTP-серверу и отправляем письмо
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
        print(f"Уведомление отправлено на {to_email}!")
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")

def send_telegram_notification(message: str):
    """
    Отправляет уведомление через Telegram Bot API.

    :param message: Текст сообщения.
    """
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Уведомление отправлено в Telegram!")
        else:
            print(f"Ошибка при отправке уведомления в Telegram: {response.text}")
    except Exception as e:
        print(f"Ошибка при отправке Telegram-уведомления: {e}")

def send_notification(subject: str, message: str, to_email: str = None):
    """
    Отправляет уведомление по email и/или через Telegram.

    :param subject: Тема уведомления (для email).
    :param message: Текст уведомления.
    :param to_email: Адрес получателя (если None, email не отправляется).
    """
    if to_email:
        send_email_notification(subject, message, to_email)
    send_telegram_notification(message)

# Пример использования
if __name__ == "__main__":
    # Отправляем уведомление
    send_notification(
        subject="Новое уведомление",
        message="Привет! Это тестовое уведомление.",
        to_email="user@example.com"
    )