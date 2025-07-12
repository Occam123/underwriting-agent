class TextRepFile:
    def __init__(self, og_type: str, filename: str, content: str):
        self.og_type = og_type
        self.filename = filename
        self.content = content


    # def dump(self) -> str:
    #     return f"--------------File--------------\n* Filename: {self.filename}\n* Content:\n{self.content}"
