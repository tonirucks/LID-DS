from abc import ABC, abstractmethod
from time import time
from typing import List

from lid_ds.utils.singleton import Singleton


class CollectorStorageService(ABC):
    @abstractmethod
    def store_dict(self, name: str, obj: dict):
        pass


class CollectorError(Exception):
    def __init__(self, message):
        self.message = message


@Singleton
class Collector:
    def __init__(self):
        self.storage = {
            "time": {}
        }
        self.name = None

    def __set_time_value(self, key: str):
        t = time()
        time_store = self.storage["time"]
        if key is "container_ready":
            time_store[key] = {
                "absolute": int(t),
                "relative": 0
            }
        elif time_store["container_ready"] is None:
            raise CollectorError("Set container_ready for relative time")
        else:
            time_store[key] = {
                "absolute": int(t),
                "relative": int(t) - time_store["container_ready"]["absolute"]
            }

    def set_meta(self, name, image, recording_time, is_exploit):
        self.name = name
        self.storage["image"] = image
        self.storage["recording_time"] = recording_time
        self.storage["exploit"] = is_exploit

    def set_exploit_start(self):
        self.__set_time_value("exploit_start")

    def set_exploit_end(self):
        self.__set_time_value("exploit_end")

    def set_container_ready(self):
        self.__set_time_value("container_ready")

    def set_warmup_end(self):
        self.__set_time_value("warmup_end")

    def write(self, storage_services: List[CollectorStorageService]):
        for service in storage_services:
            service.store_dict(self.name, self.storage)




