from .shell import Shell
from .kernel import Kernel

class System:
    def __init__(self) -> None:
        self.__kernel: Kernel = Kernel()
        self.__shell: Shell = Shell(self.__kernel)
        
    def run(self) -> None:
        while True:
            try:
                self.__shell.runInteractive()
            except Exception:
                print("Shutdown...")
                break
            self.__shell = Shell(self.__kernel) # Reboots shell



