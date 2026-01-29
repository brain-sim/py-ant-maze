class MazeElement:
    def __init__(self, name: str, token: str, value: int) -> None:
        self.name = name
        self.token = token
        self.value = value
        self._validate()

    def _validate(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("element name must be a non-empty string")
        if not isinstance(self.token, str):
            raise TypeError("element token must be a string")
        if len(self.token) != 1:
            raise ValueError("element token must be a single character")
        if self.token.isspace():
            raise ValueError("element token cannot be whitespace")
        if self.token == "|":
            raise ValueError("element token cannot be '|'")
        if not isinstance(self.value, int):
            raise TypeError("element value must be an integer")


class CellElement(MazeElement):
    pass


class WallElement(MazeElement):
    pass
