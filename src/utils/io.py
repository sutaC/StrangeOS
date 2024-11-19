from colorama import Style, Fore
from enum import Enum

class IO:
    class Styles(Enum):
        normal = "normal"
        success = "success"
        error = "error"
        warning = "warning"
        dim = "dim"

    @staticmethod
    def write(*txt, sep: str | None = " ", end: str | None = "\n", style: Styles | None = "") -> None:
        msg: str = ' '.join(txt)
        match style:
            case IO.Styles.success:
                msg = Fore.GREEN +  msg + Fore.RESET
            case IO.Styles.error:
                msg = Fore.RED +  msg + Fore.RESET
            case IO.Styles.warning:
                msg = Fore.YELLOW +  msg + Fore.RESET
            case IO.Styles.dim:
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
    
    