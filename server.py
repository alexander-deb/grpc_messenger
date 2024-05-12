from concurrent import futures
import grpc
import messenger_pb2
import messenger_pb2_grpc
import redis


class MessengerServicer(messenger_pb2_grpc.MessengerServicer):
    def __init__(self):
        self.TTL = 10
        self.redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    def Register(self, request, context):
        self.redis.sadd("clients", request.nickname_)
        return messenger_pb2.Confirmation(message_="Registered successfully")

    def SendMessage(self, request, context):
        if self.redis.sismember("clients", request.from_):
            message_key = f"msg:{request.to_}:{self.redis.incr('msg_id')}"
            message_data = f"{request.from_}:{request.text_}"

            self.redis.setex(message_key, self.TTL, message_data)

            self.redis.rpush(f"chats:{request.to_}", message_key)

            return messenger_pb2.Confirmation(message_=f"Message successfully sent from {request.from_}!")
        else:
            return messenger_pb2.Confirmation(message_="User not registered")

    def ChatStream(self, request, context):
        last_index = 0
        while True:
            keys_list = f"chats:{request.nickname_}"
            chat_length = self.redis.llen(keys_list)
            while chat_length > last_index:
                message_key = self.redis.lindex(keys_list, last_index)
                message_data = self.redis.get(message_key)
                if message_data:
                    sender, message = message_data.split(':', 1)
                    mess = messenger_pb2.Message(from_=sender, to_=request.nickname_, text_=message)
                    yield mess
                last_index += 1


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    messenger_pb2_grpc.add_MessengerServicer_to_server(MessengerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
