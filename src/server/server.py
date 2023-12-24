"""Server class"""

import logging
import socket
import sys
import time
from threading import Thread
from typing import Dict, Optional, Union

from src.tools.backend import Backend
from src.tools.commands import Commands
from src.tools.constant import IP_API, PORT_API


class Server:
    """
    This class handle server connection, send and receive data from clients in TCP
    """

    def __init__(self, host: str, port: int, conn_nb: int = 2) -> None:
        self.backend = Backend(IP_API, PORT_API)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(conn_nb)
        self.conn_dict: Dict[str, socket.socket] = {}
        self.user_dict: Dict[str, str] = {}
        Thread(target=self.launch, name="Server thread").start()

        self.hello_world(host, port)

    def hello_world(self, hostname: str, port: int) -> None:
        """
        Display server is running

        Args:
            hostname (str): hostname of the server
            port (int): port of the server
        """
        logging.info("Server is running on hostname: %s, port: %s", hostname, port)

    def launch(self) -> None:
        """
        Launch the server
        """
        time_sleep = 0.1

        try:
            while "Server connected":
                conn, addr = self.sock.accept()
                time.sleep(time_sleep)
                conn_thread = Thread(
                    target=self.create_connection,
                    args=(conn, addr),
                    name=f"{addr} thread",
                    daemon=True,
                )
                conn_thread.start()
        except (KeyboardInterrupt, ConnectionAbortedError):
            self.close_connection()

    # pylint: disable=unused-argument
    def close_connection(self, *args) -> None:
        """
        Close the connection
        """
        # close the socket
        logging.info("Server disconnected")
        self.sock.close()
        sys.exit(0)

    def read_data(self, conn: socket) -> tuple:
        """
        Read raw data from the client

        Args:
            conn (socket): socket of the client
        Returns:
            tuple: return header and payload
        """
        raw_data: bytes = b""
        header, payload = None, None
        while "Empty message":
            chunk = conn.recv(1)
            if chunk not in [b"\n", b""]:
                raw_data += chunk
            else:
                break
        if raw_data:
            header, payload = raw_data[0], raw_data[1:].decode("utf-8")
        return header, payload

    def send_data(
        self,
        conn: socket,
        header: Commands,
        payload: str,
        is_from_server: Optional[bool] = False,
    ) -> None:
        """
        Send data to the client

        Args:
            conn (socket): connection with the client
            header (Commands): header of the cmd
            payload (str): payload of the cmd
            is_from_server (Optional[bool], optional): cmd from server. Defaults to False.
        """
        message = f"server:{payload}\n" if is_from_server else f"{payload}\n"

        bytes_message = header.value.to_bytes(1, "big") + message.encode("utf-8")
        conn.send(bytes_message)

    def create_connection(self, conn: socket, addr: str) -> None:
        """
        Create a new connection

        Args:
            conn (socket): Socket of the client
            addr (str): address of the client
        """
        self.handle_new_connection(addr, conn)

        logging.debug("Connected by %s", addr)

        # Receive the data in small chunks and retransmit it
        try:
            while True:
                header, payload = self.read_data(conn)
                if not payload:
                    raise ConnectionAbortedError

                receiver = self.__match_username_and_address(addr, payload)

                if message_id := self.send_message_to_backend(header, payload):
                    payload = f"{message_id}:{payload}"

                # If receiver is home, send messages to all users
                if receiver == "home":
                    for socket_ in self.conn_dict.values():
                        self.send_data(socket_, Commands(header), payload)
                    continue

                if receiver in self.user_dict:
                    # Send to the receiver
                    self.send_data(
                        self.conn_dict[self.user_dict[receiver]],
                        Commands(header),
                        payload,
                    )
                # Send to the sender anyway
                self.send_data(
                    self.conn_dict[addr],
                    Commands(header),
                    payload,
                )
                logging.debug(
                    "Client %s: >> header: %s payload: %s", addr, header, payload
                )

        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            self._display_disconnection(conn, addr)
        except KeyError as error:
            logging.error(error)

    def send_message_to_backend(self, header: int, payload: str) -> Union[None, str]:
        """
        Send message to the API

        Args:
            header (int): header of the message
            payload (str): payload of the message
        """
        if Commands(header) == Commands.MESSAGE:
            return self._send_string_message(payload)
        if Commands(header) in [Commands.ADD_REACT, Commands.RM_REACT]:
            self._update_reaction(payload)

        return None

    def _send_string_message(self, payload: str) -> str:
        """
        Send string message to the API

        Args:
            payload (str): payload

        Returns:
            str: message_id
        """
        payload_list = payload.split(":")
        sender, receiver, message = (
            payload_list[0],
            payload_list[1],
            payload_list[2],
        )
        response_id = payload_list[3] if len(payload_list) == 4 else 0
        receiver = receiver.replace(" ", "")
        response = self.backend.send_message(sender, receiver, message, response_id)

        return response["message_id"]

    def _update_reaction(self, payload: str) -> None:
        """
        Add backend message to update reaction

        Args:
            payload (str): payload
        """
        payload_list = payload.split(":")
        _, _, message = payload_list[0], payload_list[1], payload_list[2]
        message_list = message.split(";")
        message_id, reaction_nb = message_list[0], message_list[1]
        logging.info(message)
        self.backend.update_reaction_nb(message_id, reaction_nb)

    def handle_new_connection(self, addr: str, conn: socket) -> None:
        """
        Handle a new connection with a client

        Args:
            addr (_type_): _description_
            conn (_type_): _description_
        """
        self.conn_dict[addr] = conn

        # Send nb of conn
        message = str(len(self.conn_dict))

        # Send to all connected clients
        for socket_ in self.conn_dict.values():
            self.send_data(socket_, Commands.CONN_NB, message, is_from_server=True)

    def _display_disconnection(self, conn: socket, addr: str) -> None:
        """
        Display disconnection on gui

        Args:
            conn (socket): socket of the client
            addr (str): socket address of the client
        """
        logging.debug("Connection aborted by the client")
        conn.close()
        self.conn_dict.pop(addr)

        # Remove user from user_dict
        for key, value in self.user_dict.items():
            if value == addr:
                self.user_dict.pop(key)
                break

        already_connected = len(self.conn_dict) >= 1
        if already_connected:
            for address, socket_ in self.conn_dict.items():
                if address != addr:
                    message = str(len(self.conn_dict))
                    self.send_data(
                        socket_,
                        Commands.CONN_NB,
                        message,
                        is_from_server=True,
                    )

    def __match_username_and_address(self, address: str, payload: str) -> None:
        """
        Match the IP addresse with the username in db

        Args:
            address (str): address
            payload (str): payload
        """
        username, receiver = payload.split(":")[0], payload.split(":")[1]
        receiver = receiver.replace(" ", "")
        username = username.replace(" ", "")
        if username != "home":
            self.user_dict[username] = address

        return receiver
