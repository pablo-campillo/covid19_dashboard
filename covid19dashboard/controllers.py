# Created by Pablo Campillo at 10/1/22
from datetime import datetime
from typing import List

from bokeh.models import Select, DateRangeSlider
from abc import ABC, abstractmethod

from .data_helper import VaccinationData


class Observer(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """

    @abstractmethod
    def update(self, observable) -> None:
        pass


class Observable(ABC):
    """
    The Subject interface declares a set of methods for managing subscribers.
    """

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """ Attach an observer to the subject. """
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """ Detach an observer from the subject. """
        pass

    @abstractmethod
    def notify(self) -> None:
        """ Notify all observers about an event. """
        pass


class GenericObservable(Observable):
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)


class CountrySelector(GenericObservable):

    def __init__(self, data: VaccinationData):
        super().__init__()
        self.value = "ES"
        self.controller = None
        self.vaccination_data = data

    def build(self):
        self.controller = Select(title="Country:", value=self.value, options=self.vaccination_data.data['ReportingCountry'].unique().tolist())

        self.controller.on_change("value", self.select_handler)
        return self.controller

    def select_handler(self, attr, old, new):
        self.value = new
        self.notify()


class DateRageSelector(GenericObservable):

    def __init__(self, data: VaccinationData):
        super().__init__()
        self.controller = None
        self.vaccination_data = data
        self.start_date = "ES"
        self.start_date = self.vaccination_data.data['Date'].min()
        self.end_date = self.vaccination_data.data['Date'].max()

    def build(self):
        self.controller = DateRangeSlider(value=(self.start_date, self.end_date),
                                            start=self.start_date,
                                            end=self.end_date, width=700)
        self.controller.on_change("value", self.select_handler)
        return self.controller

    def select_handler(self, attr, old, new):
        self.start_date = datetime.fromtimestamp(new[0]/1000)
        self.end_date = datetime.fromtimestamp(new[1]/1000)
        self.notify()
