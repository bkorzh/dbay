from lab_link import ReactiveModel

class Core(ReactiveModel):
    slot: int
    type: str
    name: str


class IModule(ReactiveModel):
    core: Core


