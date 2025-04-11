def generate_dto_and_manager(name, name_camel):
    return f"""

@dataclass
class {name_camel}DTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class {name_camel}Manager(BaseManager):
    def __init__(self):
        super().__init__({name_camel}, {name_camel}DTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, {name}):
        pass
    """
