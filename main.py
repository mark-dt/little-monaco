from src.tools import Tools
import src.dt_api


def main():
    tools = Tools(__file__)
    src.dt_api.DtAPI(tools)


if __name__ == "__main__":
    main()
