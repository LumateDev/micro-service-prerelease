import asyncio
import json
import os
from dotenv import load_dotenv
import logging
import aio_pika
import httpx

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("auth-service")

logger.info(f"Пробуем подключиться к RabbitMQ по параметрам: хост = {RABBITMQ_HOST}, порт = {RABBITMQ_PORT}")
RABBITMQ_URL = "amqp://guest:guest@rabbitmq/"


async def send_response_to_queue(reply_to: str, response: dict, correlation_id: str):
    """
    Отправляет ответное сообщение в указанную очередь.
    """
    try:
        logger.info(f"Отправка ответа в очередь: {reply_to}, correlation_id: {correlation_id}")
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(response).encode(),
                    correlation_id=correlation_id,
                ),
                routing_key=reply_to,
            )
        logger.info(f"Ответ успешно отправлен в очередь {reply_to}")
    except Exception as e:
        logger.error(f"Ошибка при отправке ответа в очередь {reply_to}: {e}", exc_info=True)


async def process_message(queue_name: str, message: dict, reply_to: str, correlation_id: str):
    """
    Обрабатывает сообщения из очередей регистрации и авторизации.
    """
    logger.info(f"Начата обработка сообщения из очереди: {queue_name}")
    logger.info(f"Полученные данные: {message}")
    logger.info(f"Ответ будет отправлен в очередь: {reply_to} с correlation_id: {correlation_id}")

    try:
        if queue_name == "registration_queue":
            logger.info("Обрабатываем сообщение из очереди регистрации...")
            if "email" in message and "password" in message:
                async with httpx.AsyncClient() as client:
                    registration_payload = {
                        "name": message["name"],
                        "email": message["email"],
                        "password": message["password"],
                    }
                    response = await client.post("http://backend-db:8080/auth/registration", json=registration_payload)
                    if response.status_code == 400:
                        logger.info("Пользователь с таким email уже существует.")
                        response_data = {"status": "failed", "message": response.json()["detail"]}
                    else:
                        logger.info("Регистрация прошла успешно.")
                        response_data = {"status": "success", "message": "Регистрация прошла успешно!"}
            else:
                logger.warning("Отсутствуют обязательные поля для регистрации!")
                response_data = {"status": "failed", "message": "Отсутствуют обязательные поля для регистрации!"}
        elif queue_name == "authorization_queue":
            logger.info("Обрабатываем сообщение из очереди авторизации...")
            if "email" in message and "password" in message:
                async with httpx.AsyncClient() as client:
                    login_payload = {
                        "email": message["email"],
                        "password": message["password"],
                    }
                    response = await client.post("http://backend-db:8080/auth/authorization", json=login_payload)
                    if response.status_code == 404:
                        logger.info("Пользователь не найден.")
                        response_data = {"status": "failed", "message": "Пользователь не найден!"}
                    elif response.status_code == 401:
                        logger.info("Неверный пароль.")
                        response_data = {"status": "failed", "message": "Неверный пароль!"}
                    else:
                        logger.info("Авторизация успешна.")
                        response_data = {"status": "success", "message": "Авторизация прошла успешно!"}
            else:
                logger.warning("Отсутствуют обязательные поля для авторизации!")
                response_data = {"status": "failed", "message": "Отсутствуют обязательные поля для авторизации!"}
        else:
            logger.error(f"Неизвестная очередь: {queue_name}")
            response_data = {"status": "failed", "message": "Неизвестная очередь!"}

        logger.info(f"Подготовлен ответ: {response_data}")
        await send_response_to_queue(reply_to, response_data, correlation_id)
        logger.info(f"Ответ отправлен в очередь {reply_to}")
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}", exc_info=True)

async def listen_to_queue(queue_name: str):
    """
    Слушает указанную очередь и обрабатывает входящие сообщения.
    """
    logger.info(f"Инициируем прослушивание очереди: {queue_name}")

    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)

            queue = await channel.declare_queue(queue_name, durable=True)
            logger.info(f"Начинаем прослушивание очереди: {queue_name}")

            async for message in queue:
                async with message.process():
                    try:
                        logger.info(f"Получено сообщение из {queue_name}: {message.body}")
                        data = json.loads(message.body)
                        await process_message(
                            queue_name,
                            data,
                            message.reply_to,
                            message.correlation_id,
                        )
                    except Exception as e:
                        logger.error(f"Ошибка обработки сообщения из {queue_name}: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Ошибка при подключении к RabbitMQ для {queue_name}: {e}", exc_info=True)


async def main():
    """
    Основная функция запуска прослушивания очередей.
    """
    tasks = [
        listen_to_queue("registration_queue"),
        listen_to_queue("authorization_queue"),
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    logger.info("Сервис авторизации запускается...")
    asyncio.run(main())
