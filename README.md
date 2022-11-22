# little-monaco
A `config.ini` file as follows is required in order to operate the scripts:
```
[TEST]
URL = https://
token = token

```

## Options

### Required

`-s` or `--stage`:\
Specify the stage on which to perform an action

`-env` or `--evironment`:\
Specific Dynatrace environment

### Optional

`--config` (optional):\
By default the script will try to find a `config.ini` file inside the root directory of `main.py`. Speficy the config file to read DT environment information.

`--log-path` (optional):\
Use if you want to define a target directory to store the logs, has to exist will not be created by the script

`--log-level` (optional):\
Use if you want to have a more verbose output (default INFO), possible values:

* DEBUG
* INFO
* WARNING
* ERROR

`--download (<target_folder>)` (optional):\
Downloads the configuration of the specified Dynatrace environment. Default value for this argument is `../imo-dt-environment-snapshot`

## Download

### Download usage samples:
The parameter `--download` can be omitted, and the default path will be used to just download all the config
```
python.exe .\main.py -s E -env Entwicklung 
```
```
python.exe .\main.py --log-path .\logs\ -s E -env Entwicklung --config config.ini --download
```

## Documentation
Robert R., Ingrida, Mark 2022-04-01:
Monaco like 1.7.0 Dynatrace API Endpoints
https://dynatrace-oss.github.io/dynatrace-monitoring-as-code/configuration/configTypes_tokenPermissions/

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
