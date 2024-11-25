from .taskcontroller import TaskController
from .kernel import Kernel
from .options import SysOptions

# Shell lib api interface
class Shell:
    _TASKC: TaskController
    _KERNEL: Kernel
    _location: str
    _user: str | None
    def __init__(self, kernel: Kernel, taskController: TaskController, options: SysOptions) -> None:
        pass
    def _joinPath(self, destination: str) -> str:
        pass  
    def _formatString(self, text: str) -> str:
        pass
    def _pathGetDir(self, path: str) -> str:
        pass
    def _pathGetBasename(self, path: str) -> str:
        pass
    def runFile(self, path: str) -> int:
        pass
    def runInteractive(self) -> None:
        pass