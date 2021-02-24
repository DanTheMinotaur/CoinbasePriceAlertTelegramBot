from abc import ABC, abstractmethod


class Messaging(ABC):

    @abstractmethod
    def send_message(self, *args, **kwargs):
        """ Sends message to the client"""
        pass

    @abstractmethod
    def close(self, *args, **kwargs):
        """ Closes the session """
        pass
