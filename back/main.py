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
#from utils.scheduler import start_scheduler, shutdown_scheduler

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

# Обработчик запроса на получение экзаменов
@app.get("/exams/")
async def fetch_exams():
    response = await send_and_wait_for_response(
        queue_name="exams_queue",
        message={},
        response_queue="exams_response_queue",
    )
    logger.info(f"Полученный response: {response}")
    logger.info(f"Получили список экзаменов, отправляем: {response.get("exams")}")
    return JSONResponse(content=response.get("exams"), status_code=200 if response.get("status") == "success" else 400)

@app.get("/enrolments-exams/")
async def fetch_enrolled_exams(email: str):
    response = await send_and_wait_for_response(
        queue_name="enrolments_exams_queue",
        message={"email": email},
        response_queue="enrolments_exams_response_queue",
    )
    logger.info(f"Полученный response: {response}")
    logger.info(f"Получили записи на экзамены для {email}: {response.get('enrolments-exams')}")
    return JSONResponse(
        content=response.get('enrolments-exams'),
        status_code=200 if response.get("status") == "success" else 400,
    )

@app.post("/enrolments-exams/")
async def enroll_to_exam(data: dict):
    """
    Обработчик записи на экзамен.
    """
    try:
        response = await send_and_wait_for_response(
            queue_name="enroll_to_exam_queue",
            message=data,
            response_queue="enroll_to_exam_response_queue",
        )
        logger.info(f"Запрос на запись на экзамен: {data}, Ответ: {response}")
        return JSONResponse(
            content={"message": "Запись выполнена успешно."} if response.get("status") == "success" else {"message": response.get("enrolments-exams")},
            status_code=200 if response.get("status") == "success" else 400,
        )
    except Exception as e:
        logger.error(f"Ошибка при записи на экзамен: {e}")
        return JSONResponse(content={"message": "Ошибка при записи на экзамен."}, status_code=500)

@app.delete("/enrolments-exams/")
async def cancel_exam(email: str, exam_id: int):
    """
    Обработчик отмены записи на экзамен.
    """
    try:
        response = await send_and_wait_for_response(
            queue_name="cancel_exam_queue",
            message={"email": email, "exam_id": exam_id},
            response_queue="cancel_exam_response_queue",
        )
        logger.info(f"Запрос на отмену экзамена: email={email}, exam_id={exam_id}, Ответ: {response}")
        return JSONResponse(
            content={"message": "Запись отменена успешно."} if response.get("status") == "success" else {"message": response.get("enrolments-exams")},
            status_code=200 if response.get("status") == "success" else 400,
        )
    except Exception as e:
        logger.error(f"Ошибка при отмене записи на экзамен: {e}")
        return JSONResponse(content={"message": "Ошибка при отмене записи на экзамен."}, status_code=500)

# Обработчик запроса на пересдачи
@app.get("/retakes/")
async def fetch_retakes():
    try:
        response = await send_and_wait_for_response(
            queue_name="retakes_queue",
            message={},
            response_queue="retakes_response_queue",
        )

        logger.info(f"Получили список пересдач, отправляем: {response["retakes"]}")
        return JSONResponse(content=response["retakes"], status_code=200 if response.get("status") == "success" else 400)

    except Exception as e:
        logger.error(f"Ошибка при получении списка пересдач: {e}")
        return JSONResponse(content={"message": "Ошибка сервера"}, status_code=500)

@app.get("/enrolments-retake/")
async def fetch_enrolled_retakes(email: str):
    try:
        response = await send_and_wait_for_response(
            queue_name="enrolments_retake_queue",
            message={"email": email},
            response_queue="enrolments_retake_response_queue",
        )

        logger.info(f"Получили записи на пересдачи для {email}: {response['enrolments-retake']}")
        return JSONResponse(
            content=response["enrolments-retake"],
            status_code=200 if response.get("status") == "success" else 400,
        )

    except Exception as e:
        logger.error(f"Ошибка при получении записей на пересдачи для {email}: {e}")
        return JSONResponse(content={"message": "Ошибка сервера"}, status_code=500)

@app.post("/enrolments-retake/")
async def enroll_to_retake(data: dict):
    """
    Обработчик записи на пересдачу.
    """
    try:
        response = await send_and_wait_for_response(
            queue_name="enroll_to_retake_queue",
            message=data,
            response_queue="enroll_to_retake_response_queue",
        )
        logger.info(f"Запрос на запись на пересдачу: {data}, Ответ: {response}")
        return JSONResponse(
            content={"message": "Запись на пересдачу выполнена успешно."} if response.get("status") == "success" else {"message": response.get("enrolments-retake")},
            status_code=200 if response.get("status") == "success" else 400,
        )
    except Exception as e:
        logger.error(f"Ошибка при записи на пересдачу: {e}")
        return JSONResponse(content={"message": "Ошибка при записи на пересдачу."}, status_code=500)

@app.delete("/enrolments-retake/")
async def cancel_retake(email: str, retake_id: int):
    """
    Обработчик отмены записи на пересдачу.
    """
    try:
        response = await send_and_wait_for_response(
            queue_name="cancel_retake_queue",
            message={"email": email, "retake_id": retake_id},
            response_queue="cancel_retake_response_queue",
        )
        logger.info(f"Запрос на отмену записи на пересдачу: email={email}, retake_id={retake_id}, Ответ: {response}")
        return JSONResponse(
            content={"message": "Запись на пересдачу отменена успешно."} if response.get("status") == "success" else {"message": response.get("enrolments-retake")},
            status_code=200 if response.get("status") == "success" else 400,
        )
    except Exception as e:
        logger.error(f"Ошибка при отмене записи на пересдачу: {e}")
        return JSONResponse(content={"message": "Ошибка при отмене записи на пересдачу."}, status_code=500)

if __name__ == "__main__":
    #@app.on_event("startup")
    #async def startup_event():
    #    start_scheduler()

    #@app.on_event("shutdown")
    #async def shutdown_event():
    #    shutdown_scheduler()

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
