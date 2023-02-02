from .builder import MonitorBuilder


class Manager:
    def __init__(self, builder: MonitorBuilder) -> None:
        self.__builder = builder
        
    def build(self):
        self.__builder.create_analyzer()
        self.__builder.create_monitor()
