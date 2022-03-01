# little-monaco

In order to be able to use this script an `config.ini` with following structure will be needed (`alias` is optional if not defined the environment id will be used instead):
```
[test]
token = dt0c01.xxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
URL = https://xxxxxxxx.sprint.dynatracelabs.com
alias = Sprint
```

Options

`-e` or `--env`:\
Specify the stage on which to perform an action

`--config` (optional):\
By default the script will try to find a `config.ini` file inside the root directory of `main.py`. Speficy the config file to read DT environment information.

`--log-path` (optional):\
Use if you want to define a target directory

`--log-level` (optional):\
Use if you want to have a more verbose output (defualt INFO), possible values:

* DEBUG
* INFO
* WARNING
* ERROR


## Download

Download usage sample (requires a `./logs` folder in the same directory as `main.py`):
```
python.exe .\main.py --log-path .\logs\ --env TEST --config config.ini --download
```
```
python3 main.py --log-path logs --env TEST --config config.ini --download
```


## Upload

In order to uplaod you will need to define the target repo with configuration folder/files, the structure of said repo needs to look like below exapmple:
```
.
└── config
    ├── alerting-profiles
    │    ├── porfile-A.json
    │    └── porfile-B.json
    └── management-zone
        └── zone-A.json
```

Upload usage sample:
```
python.exe .\main.py --log-path .\logs\ -s E --config config.ini --repo 'config'
```