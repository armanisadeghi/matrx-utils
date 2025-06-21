
from abc import ABC, abstractmethod


class BaseHandler(ABC):
    @abstractmethod
    def read(self, path):
        pass

    @abstractmethod
    def write(self, path, content):
        pass

    @abstractmethod
    def append(self, path, content):
        pass

    @abstractmethod
    def delete(self, path):
        pass
