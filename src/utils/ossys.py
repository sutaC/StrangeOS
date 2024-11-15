from .shell import Shell
from .kernel import Kernel
from .taskcontroller import TaskController
from traceback import print_exc
from colorama import Fore

# System
class System:
    verbose: bool = True # For debugging

    def __init__(self) -> None:
        self._TASKC: TaskController = TaskController()
        self._KERNEL: Kernel = Kernel()
        self._SHELL: Shell = Shell(self._KERNEL, self._TASKC)

    def run(self) -> None:
        self._TASKC.addTask(self._SHELL.runInteractive)
        while not self._TASKC.isEmpty():
            task = self._TASKC.getTask()
            try:
                result = task()
                if result != 0 and result is not None:
                    print(f"Task exited with code {result}")       
            except Exception as exc:
                print(Fore.RED, "Unexpected error occurred", exc, Fore.RESET, sep="\n")
                if self.verbose:
                    print_exc()
                return
        print("Closing system...")


