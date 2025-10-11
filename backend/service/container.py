from dependency_injector import containers, providers

from service.layers.application.mange_ta_main import DataAnylizer
from service.layers.infrastructure.csv_adapter import CSVAdapter


class Container(containers.DeclarativeContainer):
    csv_adapter = providers.Singleton(CSVAdapter)
    data_analyzer = providers.Singleton(DataAnylizer, csv_adapter=csv_adapter)


container = Container()
