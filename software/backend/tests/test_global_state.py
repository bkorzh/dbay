import os

from backend.initialize import GlobalState
from backend.location import DATA_DIR

if __name__ == "__main__":
    global_state = GlobalState(vsource_params=os.path.join(DATA_DIR, "vsource_params.json"))
    print(global_state)