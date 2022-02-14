from tools import Tools
import dt_api

def main():
    tools = Tools(__file__)
    dt_api.DtAPI(tools)

if __name__ == '__main__':
    main()