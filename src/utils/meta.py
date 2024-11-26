class Metadata:
    # Metadata scheme: read / write / execute
    def __init__(self, codedmeta: str | None = None) -> None:
        self.__owner = 'root'
        self.__others = {True, False, False}
        self.__users: dict[str, tuple[bool, bool, bool]] = {}
        if codedmeta is not None:
            self.setByCoded(codedmeta)

    # Private
    def __parseMetaCode(meta: str) -> tuple[bool, bool, bool]:
        if len(meta) != 3:
            raise Exception(f"Invalid metadata format `{meta}`")
        code = (False, False, False)
        for i, ch in enumerate(meta):
            if ch not in '10':
                raise Exception(f"Invalid metadata format `{meta}`")
            code[i] = ch == '1'
        return code
    
    def __stringifyMetaCode(code: tuple[bool, bool, bool]) -> str:
        meta = ''
        for val in code:
            if val:
                meta += "1"
            else:
                meta += "0"
        return meta

    # Public
    # Coded metatada scheme: <owner>:<code>|<others code>|<user>:<code>|...
    def setByCoded(self, coded: str) -> None:
        part: list[str] = coded.split("|")
        if len(part) < 2:
            raise Exception(f"Invalid metadata format `{coded}`")
        self.__users.clear()
        for i, meta in enumerate(part):
            # Others code
            if i == 1:
                continue
            [user, code] = meta.split(":")
            if not self.__isValidMetaCode(code):
                continue
            self.__users[user] = self.__parseMetaCode(code)
            # Owner
            if i == 0:
                self.__owner = user

    def getCoded(self) -> str:
        code: str = f"{self.__owner}|{self.__others}"
        for user in self.__users.keys():
            meta = self.__stringifyMetaCode(self.__users[user])
            code += f"|{user}:{meta}"
        return code
        
    def getUserMeta(self, login: str | None) -> tuple[bool, bool, bool]:
        if login is None:
            return self.__others
        meta: tuple[bool, bool, bool] | None = self.__others[login]
        if meta is None:
            return self.__others
        return meta
