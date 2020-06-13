import os

import pika
import json
import typing
from django.urls import reverse


class MessageQueueProvider:
    def __init__(self):
        self.connection_ = None
        return

    def send_confirmation(self, queue, recipient, subject, body, retry_count=5):
        if not self.connection_ or self.connection_.is_closed:
            self.connection_ = pika.BlockingConnection(
                parameters=pika.ConnectionParameters(
                    host=os.environ.get("MQ_HOST"),
                    port=int(os.environ.get("MQ_PORT")),
                    heartbeat=None,
                )
            )

        channel = self.connection_.channel()
        channel.queue_declare(queue=queue)

        body = json.dumps(
            obj={
                "recipient":   recipient,
                "subject":     subject,
                "body":        body,
                "retry_count": retry_count,
            }
        )

        channel.basic_publish(exchange="", routing_key=queue, body=body)

        return


message_queue_provider = MessageQueueProvider()


def get_notification_queue(prefix):
    notification_queues: typing.List[str] = os.environ.get("NOTIFICATION_QUEUES").split(",")

    for queue in notification_queues:
        if queue.startswith(prefix):
            return queue

    return "default"


def make_confirmation_message(view, confirmation_token, user_id):
    greeting = "<p>Hello!</p>\n"
    prefix = "<p>Please, click confirmation link below to complete your registration:</p>\n"

    host_and_port = "http://0.0.0.0" + ":" + os.environ.get("AUTH_PORT")
    confirm_registration_url = host_and_port + reverse(view, **{}) + f"?id={user_id}&token={str(confirmation_token)}"
    link = str(confirm_registration_url)

    print(confirm_registration_url)

    return "".join([greeting, prefix, link])
