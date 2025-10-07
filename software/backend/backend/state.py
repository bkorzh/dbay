from pydantic import BaseModel, Field
# from backend.addons.vsense import ChSenseState

from pydantic import BaseModel, Field

from typing import Literal, Union, Type
from typing_extensions import Annotated
import os
import importlib
import importlib.util
import sys

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__)) # needed for pyinstaller to work

class Core(BaseModel):
    slot: int
    type: str
    name: str

class IModule(BaseModel):
    core: Core


class Empty(IModule):
    module_type: Literal["empty"] = "empty"
    core: Core


from backend.modules.dac4D_spec import dac4D
from backend.modules.dac16D_spec import dac16D
from backend.modules.adc4D_spec import adc4D

modules = {"dac4D": dac4D, "dac16D": dac16D, "adc4D": adc4D}

# this dynamically loads schema for the modules from {module_name}_spec.py files in the modules directory
# if you think it's causing problems, comment it out and customize the following lines. 
# def load_models_from_directory(directory: str) -> dict[str, Type[BaseModel]]:
#     modules: dict[str, Type[BaseModel]] = {}

#     print("where AM I", os.listdir(os.path.join(os.path.dirname(sys.executable),"_internal")))
#     # print("where amy I", os.listdir(SCRIPT_PATH))

#     directory = os.path.join(SCRIPT_PATH, directory)

#     for filename in os.listdir(directory):
#         # print(filename)
#         if filename.endswith('_spec.py') and filename != '__init__.py':
#         #     module_name = filename[:-8]  # remove '_spec.py' from filename
#         #     module = importlib.import_module(f'.{module_name}_spec', package=f"backend.{directory}")
#         #     class_: Type[BaseModel] = getattr(module, module_name)
#         #     modules[module_name] = class_
        
#             module_name = filename[:-8]  # remove '_spec.py' from filename
#             module_path = os.path.join(directory, filename)
#             spec = importlib.util.spec_from_file_location(module_name, module_path) # import the class of name dac4D from dac4D_spec.py
#             if spec and spec.loader:
#                 module = importlib.util.module_from_spec(spec)
#                 spec.loader.exec_module(module)
#                 class_: Type[BaseModel] = getattr(module, module_name)
#                 modules[module_name] = class_
#     return modules

# modules = load_models_from_directory('modules')



GenericModule = Annotated[Union[Empty, *modules.values()], Field(discriminator='module_type')] # type: ignore


# uncomment below, and customize to import all the module schemas, and put each in the Union below:
# from backend.modules.dac4D_spec import dac4D
# from backend.modules.dac16D_spec import dac16D
# GenericModule = Annotated[Union[Empty, dac4D, dac16D], Field(discriminator='module_type')]

'''
NOTE: SystemState.data can NOT just be a list of IModule. Though IModule is a base class for all the modules,
it has a smaller set of fields than real modules. Pydantic would validate away the extra fields in the real modules.
You need the tagged Union[Empty, dac4D, dac16D...] to be able to validate the real modules.

'''

class SystemState(BaseModel):
    data: list[GenericModule]
    valid: bool
    dev_mode: bool
    

class VMEParams(BaseModel):
    ipaddr: str
    timeout: int
    port: int
    dev_mode: bool





