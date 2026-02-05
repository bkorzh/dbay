from pydantic import BaseModel

class Core(BaseModel):
    slot: int
    type: str
    name: str


class IModule(BaseModel):
    core: Core


