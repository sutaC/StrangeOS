from colorama import Style, Fore

class IO:
    @staticmethod
    def write(*txt, sep: str | None = " ", end: str | None = "\n", style: str | None = "") -> None:
        msg: str = ' '.join(txt)
        match style:
            case "success":
                msg = Fore.GREEN +  msg + Fore.RESET
            case "error":
                msg = Fore.RED +  msg + Fore.RESET
            case "warning":
                msg = Fore.YELLOW +  msg + Fore.RESET
            case "dim":
                msg = Fore.BLACK +  msg + Fore.RESET
                msg = Style.DIM +  msg + Style.RESET_ALL
        print(msg, sep=sep, end=end)

    @staticmethod
    def read(prompt: str = "") -> str:
        result: str = None
        while result is None:
            try:
                result = input(prompt)
            except KeyboardInterrupt:
                IO.write("\nTo exit os type `exit`")
        return result