from os import get_terminal_size
from utils.kernel import MissingNodeException, NodeTypeException
from utils.io import IO

def main(shell, segments: list[str]) -> int:
    # Get file
    if len(segments) < 2:
        IO.write("Missing argumnent - path")
        return 1
    path: str = shell._joinPath(segments[1])
    nodeId: int 
    try:
        nodeId = shell._KERNEL.get_node_path(path)
        if not shell._KERNEL.is_file(nodeId):
            raise NodeTypeException
    except (NodeTypeException, MissingNodeException):
        IO.write(f"Could not open file - {path}")
        return 1
    # Editor
    cont: list[str] = shell._KERNEL.read_file(nodeId).splitlines()
    while True:
        # Displays cont
        IO.write("\n" * (get_terminal_size().lines + 1))
        for i, line in enumerate(cont):
            spaces: str = (len(str(len(cont))) - len(str(i)) + 1) * ' '
            IO.write(f"{i}{spaces}|{line}")
        # Action
        ins: str = None
        try:
            ins = input(":")
        except KeyboardInterrupt:
            break
        print(ins[0])
        if len(ins) == 0:
            continue
        match ins[0]:
            case 'q': # quit
                break
            case 'w': # write
                idx: int
                try:
                    idx = int(ins[:ins.find(" ")])
                except:
                    continue
                if idx < 0:
                    continue
                txt = ins[ins.find(" "):]
                while idx <= len(cont):
                    cont.append("")
                cont[idx] = txt
                shell._KERNEL.write_to_file(nodeId, '\n'.join(cont))
    return 0
