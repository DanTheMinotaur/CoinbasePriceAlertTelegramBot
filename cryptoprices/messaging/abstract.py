from abc import ABC, abstractmethod


class Messaging(ABC):

    @abstractmethod
    async def send_message(self, *args, **kwargs):
        """ Sends message to the client"""
        pass

    @abstractmethod
    async def close(self, *args, **kwargs):
        """ Closes the session """
        pass
