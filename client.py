import threading

import grpc
import messenger_pb2
import messenger_pb2_grpc


class Client:
    def __init__(self):
        self.nickname = None
        self.printing = None
        self.receiving = None
        self.to_print = []

    def listen_for_messages(self, client, nickname_):
        while True:
            for message in client.ChatStream(messenger_pb2.User(nickname_=nickname_)):
                self.to_print.append(message)

    def print(self):
        while True:
            if self.printing and len(self.to_print) > 0:
                print("---New messages---")
                to_print = self.to_print.copy()
                for message in to_print:
                    print(f"\n{message.from_}:")
                    print(message.text_ + "\n")
                    self.to_print.remove(message)

    def main(self):
        with grpc.insecure_channel('localhost:50051') as channel:
            grpc_client = messenger_pb2_grpc.MessengerStub(channel)
            self.nickname = input("Enter your nickname: ")
            print(grpc_client.Register(messenger_pb2.User(nickname_=self.nickname)).message_)
            threading.Thread(target=self.listen_for_messages,
                             kwargs={"client": grpc_client, "nickname_": self.nickname},
                             daemon=True).start()
            threading.Thread(target=self.print,
                             daemon=True).start()
            print("If you want to send message, press any key whenever you want")
            while True:
                self.printing = True
                flag = input()
                self.printing = False
                to = input("Enter address: ")
                text = input("Enter your message: ")
                response = grpc_client.SendMessage(messenger_pb2.Message(from_=self.nickname, to_=to, text_=text))
                print(response.message_)


if __name__ == '__main__':
    client = Client()
    client.main()
