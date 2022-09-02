from src.tools import Tools
from src.dt_api import DtAPI



def main():
    tools = Tools(__file__)
    DtAPI(tools)


if __name__ == "__main__":
    main()
