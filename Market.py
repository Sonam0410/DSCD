from concurrent import futures
import register

import sys
import grpc
import Market_pb2
import Market_pb2_grpc

register = register.getregister("registrar")
register.setLevel(register.INFO)
MAXSERVERS = 5  # default, changeable by command line arg

registered = Market_pb2.Server_book()


class Maintain(Market_pb2_grpc.MaintainServicer):
    def RegisterServer(self, request, context):
        register.info(
            "JOIN REQUEST FROM %s",
            context.peer(),
        )
        if len(registered.servers) >= MAXSERVERS:
            return Market_pb2.Success(value=False)
        if any(
            i.id == request.id or i.addr == request.addr for i in registered.servers
        ):
            return Market_pb2.Success(value=False)
        new_server = registered.servers.add()
        new_server.id = request.id
        new_server.addr = request.addr
        return Market_pb2.Success(value=True)

    def GetServerList(self, request, context):
        register.info(
            "SERVER LIST REQUEST FROM %s with id %s",
            context.peer(),
            request.id,
        )
        return registered
        

def serve():
    port = "21337"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Market_pb2_grpc.add_MaintainServicer_to_server(Maintain(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Registry started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    # get sys args

    if len(sys.argv) > 1:
        try:
            MAXSERVERS = int(sys.argv[1])
        except ValueError:
            print("Invalid number of servers")
            print("Usage: python registry_server.py [number of servers]")
            sys.exit(1)
    register.basicConfig()
    serve()
