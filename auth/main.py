import asyncio
import json
import os
from dotenv import load_dotenv
import logging
import aio_pika

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("auth-service")

logger.info(f"Пробуем подключиться к RabbitMQ по параметрам: хост = {RABBITMQ_HOST}, порт = {RABBITMQ_PORT}")
RABBITMQ_URL = f"amqp://guest:guest@rabbitmq/"


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
            if "email" in message:
                if message["email"] == "test@example.com":
                    logger.info("Email совпадает с запрещённым для регистрации.")
                    response = {"status": "failed", "message": "Пользователь с таким Email уже зарегистрирован!"}
                else:
                    logger.info("Email прошёл проверку, регистрация успешна.")
                    response = {"status": "success", "message": "Регистрация прошла успешно!"}
            else:
                logger.warning("Отсутствуют обязательные поля для регистрации!")
                response = {"status": "failed", "message": "Отсутствуют обязательные поля для регистрации!"}
        elif queue_name == "authorization_queue":
            logger.info("Обрабатываем сообщение из очереди авторизации...")
            if "email" in message:
                if message["email"] == "test@example.com":
                    logger.info("Email совпадает, авторизация успешна.")
                    response = {"status": "success", "message": "Авторизация прошла успешно!"}
                else:
                    logger.info("Email не найден, авторизация провалена.")
                    response = {"status": "failed", "message": "Пользователь с таким Email не найден!"}
            else:
                logger.warning("Отсутствуют обязательные поля для авторизации!")
                response = {"status": "failed", "message": "Отсутствуют обязательные поля для авторизации!"}
        else:
            logger.error(f"Неизвестная очередь: {queue_name}")
            response = {"status": "failed", "message": "Неизвестная очередь!"}

        logger.info(f"Подготовлен ответ: {response}")
        await send_response_to_queue(reply_to, response, correlation_id)
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
