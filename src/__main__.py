"""Entry point"""

from src.server.server import Server
from src.tools.constant import IP_SERVER, PORT_SERVER
from src.tools.logger import setup_logger

if __name__ == "__main__":
    setup_logger("server.log")
    Server(IP_SERVER, PORT_SERVER)
