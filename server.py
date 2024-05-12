from concurrent import futures
import grpc
import messenger_pb2
import messenger_pb2_grpc
from collections import defaultdict

class MessengerServicer(messenger_pb2_grpc.MessengerServicer):
    def __init__(self):
        self.clients = {}
        self.chats = defaultdict(list)
        self.chats["alex"].append(messenger_pb2.Message(from_="alex", to_="alex", text_="test"))

    def Register(self, request, context):
        self.clients[request.nickname_] = context
        return messenger_pb2.Confirmation(message_="Registered successfully")

    def SendMessage(self, request, context):
        if request.from_ in self.clients:
            self.chats[request.to_].append(request)
            return messenger_pb2.Confirmation(message_=f"Message successfully sent!")
        return messenger_pb2.Confirmation(message_="User not registered", )

    def ChatStream(self, request, context):
        lastindex = 0
        while True:
            while len(self.chats[request.nickname_]) > lastindex:
                mess = self.chats[request.nickname_][lastindex]
                lastindex += 1
                yield mess


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    messenger_pb2_grpc.add_MessengerServicer_to_server(MessengerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
