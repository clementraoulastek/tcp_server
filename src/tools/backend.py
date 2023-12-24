"""Module to communicate with the API"""

from typing import Optional, Union

import requests

# pylint: disable=no-name-in-module
from PySide6.QtWidgets import QFileDialog, QMainWindow


class Backend:
    """
    This class handle API connection, send and receive data from API
    """

    def __init__(self, ip: str, port: str, parent: Union[QMainWindow, None] = None):
        self.parent = parent
        self.ip = ip
        self.port = port

    def send_login_form(self, username: str, password: str) -> bool:
        """
        Send login form to the API

        Args:
            username (str): the username
            password (str): the password

        Returns:
            bool: True if the login is successful, False otherwise
        """
        endpoint = f"http://{self.ip}:{self.port}/user/"
        response = requests.get(
            url=f"{endpoint}{username}?password={password}", timeout=10
        )
        is_connected: bool = False
        if response.status_code == 200 and response.content:
            is_connected: bool = response.json()["is_connected"]

        return response.status_code, is_connected

    def send_login_status(self, username: str, status: bool) -> bool:
        """
        Send login status to the API

        Args:
            username (str): the username
            status (bool): the status

        Returns:
            bool: True if the login status is successful, False otherwise
        """
        endpoint = (
            f"http://{self.ip}:{self.port}/user/{username}/?is_connected={status}"
        )
        response = requests.patch(url=endpoint, timeout=10)

        return response.status_code == 200

    def send_register_form(self, username: str, password: str) -> bool:
        """
        Send register form to the API

        Args:
            username (str): the username
            password (str): the password

        Returns:
            bool: True if the register is successful, False otherwise
        """
        endpoint = f"http://{self.ip}:{self.port}/register"
        data = {"username": username, "password": password}
        header = {"Accept": "application/json"}
        response = requests.post(url=endpoint, headers=header, json=data, timeout=10)
        return response.status_code == 200

    def send_user_icon(
        self, username: str, picture_path: str = None
    ) -> Union[None, bool]:
        """
        Send user icon to the API

        Args:
            username (str): the username
            picture_path (str, optional): the picture path. Defaults to None.

        Returns:
            Union[None, bool]: True if the user icon is successful, False otherwise
        """
        # pylint: disable=fixme
        path = picture_path or QFileDialog.getOpenFileName(
            self.parent,
        )  # TODO: To remove from here
        if not path[0]:
            return None
        endpoint = f"http://{self.ip}:{self.port}/user/{username}"

        with open(path[0], "rb") as file:
            files = {"file": file}
            response = requests.put(url=endpoint, files=files, timeout=10)

        return response.status_code == 200

    def get_user_icon(self, username: str) -> Union[bool, bytes]:
        """
        Get user icon from the API

        Args:
            username (str): the username

        Returns:
            Union[bool, bytes]: the user icon if the request is successful, False otherwise
        """
        endpoint = f"http://{self.ip}:{self.port}/user/"
        response = requests.get(url=f"{endpoint}{username}/picture", timeout=10)
        if response.status_code == 200 and response.content:
            return response.content
        return False

    def get_all_users_username(self) -> Union[bool, dict]:
        """
        Get all users username from the API

        Returns:
            Union[bool, dict]: the users username if the request is successful, False otherwise
        """
        endpoint = f"http://{self.ip}:{self.port}/users"
        response = requests.get(url=f"{endpoint}/username", timeout=10)
        if response.status_code == 200 and response.content:
            return response.json()
        return False

    def get_older_messages(self) -> Union[bool, dict]:
        """
        Get older messages from the API

        Returns:
            Union[bool, dict]: the older messages if the request is successful, False otherwise
        """
        endpoint = f"http://{self.ip}:{self.port}/messages/"
        response = requests.get(url=endpoint, timeout=10)
        if response.status_code == 200 and response.content:
            return response.json()
        return False

    def send_message(
        self,
        username: str,
        receiver: str,
        message: str,
        response_id: Optional[int] = None,
    ) -> Union[None, dict]:
        """
        Send message to the API

        Args:
            username (str): the username
            receiver (str): the receiver
            message (str): the message
            response_id (Optional[int], optional): Response ID. Defaults to None.

        Returns:
            Union[None, dict]: the message if the request is successful, None otherwise
        """
        endpoint = f"http://{self.ip}:{self.port}/messages/"
        data = {
            "sender": username,
            "receiver": receiver,
            "message": message,
            "response_id": response_id,
        }
        header = {"Accept": "application/json"}
        response = requests.post(url=endpoint, headers=header, json=data, timeout=10)

        return response.json() if response.status_code == 200 else None

    def update_reaction_nb(self, message_id: int, reaction_nb: int) -> int:
        """
        Update reaction number of a message

        Args:
            message_id (int): the message ID
            reaction_nb (int): the reaction number

        Returns:
            int: the status code
        """
        # pylint: disable=line-too-long
        endpoint = f"http://{self.ip}:{self.port}/messages/{message_id}/reaction/?new_reaction_nb={reaction_nb}"
        response = requests.patch(url=endpoint, timeout=10)
        return response.status_code

    def update_is_readed_status(
        self, sender: str, receiver: str, is_readed: Optional[bool] = True
    ) -> int:
        """
        Update is readed status of a message

        Args:
            sender (str): username of the sender
            receiver (str): username of the receiver
            is_readed (Optional[bool], optional): if the message is readed. Defaults to True.

        Returns:
            int: the status code
        """
        # pylint: disable=line-too-long
        endpoint = f"http://{self.ip}:{self.port}/messages/readed/?sender={sender}&receiver={receiver}&is_readed={is_readed}"
        response = requests.patch(url=endpoint, timeout=10)
        return response.status_code
