from .shell import Shell
from .kernel import Kernel
from .taskcontroller import TaskController
from traceback import print_exc
from colorama import Fore
from .options import SysOptions, getDefaultOptions, loadOptions 



# System
class System:
    def __init__(self) -> None:
        print(Fore.BLACK, "Starting system...",Fore.RESET)
        # Loads options
        self._OPTIONS: SysOptions = getDefaultOptions()
        opts = loadOptions()
        if opts is None:
            print(Fore.YELLOW, "Due to missing custom options system loads default options", Fore.RESET)
        else:
            print(Fore.BLACK, "Loading custom options...", Fore.RESET)
            self._OPTIONS.update(opts)
        # Init subsystems
        self._TASKC: TaskController = TaskController()
        self._KERNEL: Kernel = Kernel(self._OPTIONS)
        self._SHELL: Shell = Shell(self._KERNEL, self._TASKC, self._OPTIONS)

    def run(self) -> None:
        self._TASKC.addTask(self._SHELL.runInteractive)
        while not self._TASKC.isEmpty():
            task = self._TASKC.getTask()
            try:
                result = task()
                if result != 0 and result is not None:
                    print(Fore.BLACK, f"Task exited with code {result}", Fore.RESET)       
            except Exception as exc:
                print(Fore.RED, "Unexpected error occurred", exc, Fore.RESET, sep="\n")
                if self._OPTIONS["verbose"]:
                    print_exc()
                    print() # Whitespace
                return
        print(Fore.BLACK, "Closing system...", Fore.RESET)


