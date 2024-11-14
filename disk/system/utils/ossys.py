from .shell import Shell

class System:
    __shell: Shell

    def __init__(self) -> None:
        pass

    def run(self) -> None:
        print("Starting os...")
        while True:
            print("Starting os shell session...")
            self.__shell = Shell()
            try:
                self.__shell.runInteractive()
            except:
                print("Shutdown...")
                break


