import pika
import threading
import random
import os
import time
import signal
import logging
from db import *


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


user = os.getenv("user", "guest")
password = os.getenv("password", "guest")
host = os.getenv("host", "localhost")
port = int(os.getenv("port", 5672))
send_queue = os.getenv("send_queue")
receive_queue = os.getenv("receive_queue")
container_nm = os.getenv("container_name")

credentials = pika.PlainCredentials(user, password)
parameters = pika.ConnectionParameters(host, port, '/', credentials)
shutdown_flag = threading.Event()


current_score:int = get_scores(container_nm)


def create_channel():
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=receive_queue)
    channel.queue_declare(queue=send_queue)
    return channel

def publish_random_numbers():
    while not shutdown_flag.is_set():
        try:
            channel = create_channel()
            random_number = random.randint(1, 4)
            channel.basic_publish(exchange='', routing_key=send_queue, body=str(random_number))
            logger.warning(f" [x] {container_nm} container  sent this number = {random_number}") 
            time.sleep(1)
            channel.close()
        except pika.exceptions.AMQPConnectionError as e:
            logger.warning(f"Connection error: {e}")
            time.sleep(15)  # Wait before retrying




def start_consuming():
        channel = create_channel()
        def callback(ch, method, properties, body):
            guess = random.randint(1, 4)
            if int(body) == guess:
                logger.warning(f" [x] {container_nm} guessed {guess} and won , number is true")
                global current_score 
                current_score += 1
                upsert_score(container_nm,current_score)
            else:
                logger.warning(f" [x] {container_nm} Guessed {guess} and lost , number is = {int(body)}")
        channel.basic_consume(queue=receive_queue, on_message_callback=callback,auto_ack=True)
        logger.warning("Starting Pika consuming thread")
        channel.start_consuming()



def signal_handler(sig, frame):
    logger.warning("Shutdown signal received. Exiting...")
    shutdown_flag.set()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
consumer_thread = threading.Thread(target=start_consuming, daemon=True)
consumer_thread.start()
publish_random_numbers()
consumer_thread.join()
