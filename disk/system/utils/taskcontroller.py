from queue import Queue
from types import FunctionType

class TaskController:
    def __init__(self) -> None:
        self.__tasks: Queue[FunctionType] = Queue()
        
    def addTask(self, task: FunctionType) -> None:
        self.__tasks.put(task)

    def emptyTasks(self) -> None:
        self.__tasks = Queue()

    def isEmpty(self) -> None:
        return self.__tasks.empty()

    def getTask(self) -> FunctionType:
        return self.__tasks.get()