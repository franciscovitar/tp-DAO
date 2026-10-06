from abc import ABC, abstractmethod
from datetime import datetime


class Subject:

    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)


class Observer(ABC):

    @abstractmethod
    def update(self, subject):
        pass


class HistorialRemitoObserver(Observer):

    def __init__(self, cursor):
        self.cursor = cursor

    def update(self, subject):
        self.cursor.execute("""
            INSERT INTO historial_remito (remito_id, estado, fecha_hora)
            VALUES (?, ?, ?)
        """, (subject.id, subject.estado,
              datetime.now().isoformat(timespec="seconds")))
