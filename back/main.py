from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import aio_pika
import asyncio
import logging
import json
import uuid
from models import User

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("backend-service")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RABBITMQ_URL = "amqp://guest:guest@rabbitmq/"

async def send_and_wait_for_response(queue_name: str, message: dict, response_queue: str):
    """
    Отправляет сообщение в указанную очередь и ожидает ответа.
    """
    correlation_id = str(uuid.uuid4())
    logger.info(f"Генерация Correlation ID: {correlation_id}")
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    
    try:
        async with connection:
            channel = await connection.channel()
            await channel.declare_queue(queue_name, durable=True)
            await channel.declare_queue(response_queue, durable=True)

            response_event = asyncio.Event()
            response_data = None

            # Callback для получения ответа
            async def on_message(message: aio_pika.IncomingMessage):
                nonlocal response_data
                logger.info(f"Пробуем получить ответ, сверяем message.correlation_id ({message.correlation_id}) с correlation_id ({correlation_id})")
                if message.correlation_id == correlation_id:
                    response_data = json.loads(message.body.decode())
                    await message.ack()
                    response_event.set()

            # Подписка на очередь с ответами
            await channel.set_qos(prefetch_count=1)
            response_queue_obj = await channel.get_queue(response_queue)
            await response_queue_obj.consume(on_message)

            # Отправка сообщения
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    correlation_id=correlation_id,
                    reply_to=response_queue,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=queue_name,
            )
            logger.info(f"Сообщение отправлено в очередь {queue_name} с Correlation ID: {correlation_id}")

            # Ожидание ответа
            await response_event.wait()
            logger.info(f"Ответ получен: {response_data}")
            return response_data
    except Exception as e:
        logger.error(f"Ошибка при работе с RabbitMQ: {e}")
        raise


# Обработчик регистрации
@app.post("/registration")
async def registration_handler(user: User):
    logger.info(f"Получены данные для регистрации: {user.email}, {user.password}")

    try:
        response = await send_and_wait_for_response(
            queue_name="registration_queue",
            message={"name": user.name, "email": user.email, "password": user.password},
            response_queue="registration_response_queue",
        )

        # Ответ от сервиса регистрации
        return JSONResponse(content=response, status_code=200 if response.get("status") == "success" else 400)

    except Exception as e:
        logger.error(f"Ошибка при обработке регистрации: {e}")
        return JSONResponse(content={"message": "Ошибка сервера"}, status_code=500)

# Обработчик авторизации
@app.post("/authorization")
async def authorization_handler(user: User):
    logger.info(f"Получены данные для авторизации: {user.email}, {user.password}")

    try:
        response = await send_and_wait_for_response(
            queue_name="authorization_queue",
            message={"email": user.email, "password": user.password},
            response_queue="authorization_response_queue",
        )

        # Ответ от сервиса авторизации
        return JSONResponse(content=response, status_code=200 if response.get("status") == "success" else 400)

    except Exception as e:
        logger.error(f"Ошибка при обработке авторизации: {e}")
        return JSONResponse(content={"message": "Ошибка сервера"}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
