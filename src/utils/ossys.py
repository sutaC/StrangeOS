from .shell import Shell
from .kernel import Kernel
from .taskcontroller import TaskController
from .io import IO
from traceback import print_exc
from .options import SysOptions, getDefaultOptions, loadOptions 

# System
class System:
    def __init__(self) -> None:
        IO.write("Starting system...", style=IO.Styles.dim)
        # Loads options
        self._OPTIONS: SysOptions = getDefaultOptions()
        opts = loadOptions()
        if opts is None:
            IO.write("Due to missing custom options system loads default options", style=IO.Styles.warning)
        else:
            IO.write("Loading options...", style=IO.Styles.dim)
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
                    IO.write(f"Task exited with code {result}", style=IO.Styles.dim)       
            except Exception as exc:
                IO.write(f"\nUnexpected error occurred\n{exc}\n", style=IO.Styles.error)
                if self._OPTIONS["verbose"]:
                    print_exc()
                    IO.write() # Whitespace
                return
        IO.write("\nClosing system...", style=IO.Styles.dim)


