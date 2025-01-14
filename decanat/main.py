import asyncio
import json
import os
import logging
import aio_pika
import httpx
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = "amqp://guest:guest@rabbitmq/"
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("exams-service")

async def send_response_to_queue(reply_to: str, response: dict, correlation_id: str):
    """
    Отправляет ответное сообщение в указанную очередь.
    """
    try:
        logger.info(f"Отправка ответа в очередь: {reply_to}, correlation_id: {correlation_id}")
        connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
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
    Обрабатывает сообщения из очередей для экзаменов и пересдач.
    """
    logger.info(f"Начата обработка сообщения из очереди: {queue_name}")
    logger.info(f"Полученные данные: {message}")
    logger.info(f"Ответ будет отправлен в очередь: {reply_to} с correlation_id: {correlation_id}")
    
    try:
        logger.info(f"Получено сообщение из очереди: {queue_name}")
        logger.info(f"Содержимое сообщения: {message}")
        if queue_name == "exams_queue":
            logger.info("Обрабатываем сообщение из очереди exams_queue")
            async with httpx.AsyncClient() as client:
                response = await client.get("http://backend-db:8080/exams/")
                if response.status_code == 400:
                    logger.info("Не удалось получить список экзаменов.")
                    response_data = {"status": "failed", "message": response.json().get("detail", "Неизвестная ошибка")}
                elif response.status_code == 200:
                    logger.info(f"Успешно получили список экзаменов: {response.json()}")
                    response_data = {"status": "success", "exams": response.json()}
                else:
                    logger.info(f"Неожиданный статус-код: {response.status_code}")
                    response_data = {"status": "failed", "message": f"Unexpected status code: {response.status_code}"}
        elif queue_name == "enrolments_exams_queue":
            logger.info("Обрабатываем запрос на записи на экзамены...")
            email = message.get("email")
            if not email:
                response_data = {"status": "failed", "message": "Отсутствует email"}
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"http://backend-db:8080/enrolments-exams/?email={email}")
                    if response.status_code == 400:
                        logger.info(f"Не удалось получить записи на экзамены для {email}.")
                        response_data = {"status": "failed", "message": response.json().get("detail", "Неизвестная ошибка")}
                    elif response.status_code == 200:
                        logger.info(f"Успешно получили записи на экзамены для {email}: {response.json()}")
                        response_data = {"status": "success", "enrolments-exams": response.json()}
                    else:
                        logger.info(f"Неожиданный статус-код: {response.status_code}")
                        response_data = {"status": "failed", "message": f"Unexpected status code: {response.status_code}"}
        elif queue_name == "enroll_to_exam_queue":
            logger.info("Обрабатываем запрос на запись на экзамен...")
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post("http://backend-db:8080/enrolments-exams/", json=message)
                    if response.status_code == 200:
                        logger.info(f"Успешная запись на экзамен: {message}")
                        response_data = {"status": "success"}
                    else:
                        logger.error(f"Ошибка записи на экзамен: {response.json()}")
                        response_data = {"status": "failed", "enrolments-exams": response.json().get("detail", "Неизвестная ошибка")}
            except Exception as e:
                logger.error(f"Ошибка при записи на экзамен: {e}", exc_info=True)
                response_data = {"status": "failed", "message": "Ошибка при записи на экзамен"}
        elif queue_name == "cancel_exam_queue":
            logger.info("Обрабатываем запрос на отмену записи на экзамен...")
            try:
                email = message.get("email")
                exam_id = message.get("exam_id")
                if not email or not exam_id:
                    response_data = {"status": "failed", "message": "Отсутствуют необходимые данные (email или exam_id)"}
                else:
                    async with httpx.AsyncClient() as client:
                        response = await client.delete(f"http://backend-db:8080/enrolments-exams/?email={email}&exam_id={exam_id}")
                        if response.status_code == 200:
                            logger.info(f"Успешная отмена записи на экзамен: email={email}, exam_id={exam_id}")
                            response_data = {"status": "success"}
                        else:
                            logger.error(f"Ошибка отмены записи на экзамен: {response.json()}")
                            response_data = {"status": "failed", "enrolments-exams": response.json().get("detail", "Неизвестная ошибка")}
            except Exception as e:
                logger.error(f"Ошибка при отмене записи на экзамен: {e}", exc_info=True)
                response_data = {"status": "failed", "message": "Ошибка при отмене записи на экзамен"}
        elif queue_name == "retakes_queue":
            logger.info("Обрабатываем сообщение из очереди retakes_queue")
            async with httpx.AsyncClient() as client:
                response = await client.get("http://backend-db:8080/retakes/")
                if response.status_code == 400:
                    logger.info("Не удалось получить список пересдач.")
                    response_data = {"status": "failed", "message": response.json().get("detail", "Неизвестная ошибка")}
                elif response.status_code == 200:
                    logger.info(f"Успешно получили список пересдач: {response.json()}")
                    response_data = {"status": "success", "retakes": response.json()}
                else:
                    logger.info(f"Неожиданный статус-код: {response.status_code}")
                    response_data = {"status": "failed", "message": f"Unexpected status code: {response.status_code}"}
        elif queue_name == "enrolments_retake_queue":
            logger.info("Обрабатываем запрос на записи на пересдачи...")
            email = message.get("email")
            if not email:
                response_data = {"status": "failed", "message": "Отсутствует email"}
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"http://backend-db:8080/enrolments-retake/?email={email}")
                    if response.status_code == 400:
                        logger.info(f"Не удалось получить записи на пересдачи для {email}.")
                        response_data = {"status": "failed", "message": response.json().get("detail", "Неизвестная ошибка")}
                    elif response.status_code == 200:
                        logger.info(f"Успешно получили записи на пересдачи для {email}: {response.json()}")
                        response_data = {"status": "success", "enrolments-retake": response.json()}
                    else:
                        logger.info(f"Неожиданный статус-код: {response.status_code}")
                        response_data = {"status": "failed", "message": f"Unexpected status code: {response.status_code}"}
        elif queue_name == "enroll_to_retake_queue":
            logger.info("Обрабатываем запрос на запись на пересдачу...")
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post("http://backend-db:8080/enrolments-retake/", json=message)
                    if response.status_code == 200:
                        logger.info(f"Успешная запись на пересдачу: {message}")
                        response_data = {"status": "success"}
                    else:
                        logger.error(f"Ошибка записи на пересдачу: {response.json()}")
                        response_data = {"status": "failed", "enrolments-retake": response.json().get("detail", "Неизвестная ошибка")}
            except Exception as e:
                logger.error(f"Ошибка при записи на пересдачу: {e}", exc_info=True)
                response_data = {"status": "failed", "message": "Ошибка при записи на пересдачу"}
        elif queue_name == "cancel_retake_queue":
            logger.info("Обрабатываем запрос на отмену записи на пересдачу...")
            try:
                email = message.get("email")
                retake_id = message.get("retake_id")
                if not email or not retake_id:
                    response_data = {"status": "failed", "message": "Отсутствуют необходимые данные (email или retake_id)"}
                else:
                    async with httpx.AsyncClient() as client:
                        response = await client.delete(f"http://backend-db:8080/enrolments-retake/?email={email}&retake_id={retake_id}")
                        if response.status_code == 200:
                            logger.info(f"Успешная отмена записи на пересдачу: email={email}, retake_id={retake_id}")
                            response_data = {"status": "success"}
                        else:
                            logger.error(f"Ошибка отмены записи на пересдачу: {response.json()}")
                            response_data = {"status": "failed", "enrolments-retake": response.json().get("detail", "Неизвестная ошибка")}
            except Exception as e:
                logger.error(f"Ошибка при отмене записи на пересдачу: {e}", exc_info=True)
                response_data = {"status": "failed", "message": "Ошибка при отмене записи на пересдачу"}
        else:
            response_data = {"status": "error", "message": "Неизвестная очередь"}
            logger.info(f"Пришли данные В ELSE: {response}")

        await send_response_to_queue(reply_to, response_data, correlation_id)

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)

async def listen_to_queue(queue_name: str):
    """
    Слушает указанную очередь и обрабатывает входящие сообщения.
    """
    logger.info(f"Инициируем прослушивание очереди: {queue_name}")

    try:
        connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
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
    tasks = [
        listen_to_queue("exams_queue"),
        listen_to_queue("enrolments_exams_queue"),
        listen_to_queue("retakes_queue"),
        listen_to_queue("enrolments_retake_queue"),
        listen_to_queue("enroll_to_exam_queue"),
        listen_to_queue("cancel_exam_queue"),
        listen_to_queue("enroll_to_retake_queue"),
        listen_to_queue("cancel_retake_queue"),
    ]
    await asyncio.gather(*tasks)

    logger.info("Сервис для работы с очередями запущен")
    await asyncio.Future()


if __name__ == "__main__":
    logger.info("Сервис-деканат запускается...")
    asyncio.run(main())
