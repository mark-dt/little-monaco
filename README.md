# little-monaco
Make quick snapshots of your dynatrace environments.

A `config.ini` file as follows is required in order to operate the scripts:
```
[TEST]
URL = https://xxxxxxxx.sprint.dynatracelabs.com
Token = dt0c01.xxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Options

### Required

`-e` or `--evironment`:\
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
Downloads the configuration of the specified Dynatrace environment. Default value for this argument is `./download`

## Download

### Download usage samples:
The parameter `--download` can be omitted, and the default path will be used to just download all the config
```
$ python3 .\main.py -e TEST
2022-09-02 17:24:00,972 [INFO] Downloading alerting-profile
Progress: |██████████████████████████████████████████████████| 8/8 Complete
2022-09-02 17:24:02,202 [INFO] Downloading app-detection-rule
Progress: |██████████████████████████████████████████████████| 281/281 Complete
2022-09-02 17:25:06,432 [INFO] Downloading application-web
Progress: |██████████████████████████████████████████████████| 166/166 Complete
2022-09-02 17:25:49,386 [INFO] Downloading application-web-data-privacy
2022-09-02 17:25:49,539 [INFO] Downloading auto-tag
Progress: |██████████████████████████████████████████████████| 17/17 Complete
2022-09-02 17:25:52,832 [INFO] Downloading custom-device
Progress: |██████████████████████████████████████████████████| 45/45 Complete
2022-09-02 17:26:04,283 [INFO] Downloading custom-service-old
Progress: |██████████████████████████████████████████████████| 21/21 Complete
2022-09-02 17:26:11,861 [INFO] Downloading anomaly-detection-disk-event
Progress: |██████████████████████████████████████████████████| 11/11 Complete
2022-09-02 17:26:13,586 [INFO] Downloading anomaly-detection-metrics
Progress: |██████████████████████████████████████████████████| 194/194 Complete
2022-09-02 17:26:59,093 [INFO] Downloading extensions
Progress: |██████████████████████████████████████████████████| 41/41 Complete
2022-09-02 17:27:14,808 [INFO] Downloading management-zone
Progress: |██████████████████████████████████████████████████| 511/511 Complete
2022-09-02 17:29:05,531 [INFO] Downloading notification
Progress: |██████████████████████████████████████████████████| 7/7 Complete
2022-09-02 17:29:06,596 [INFO] Downloading maintenance-window
Progress: |██████████████████████████████████████████████████| 100/100 Complete
2022-09-02 17:29:07,449 [INFO] Downloading declarative-grouping
Progress: |██████████████████████████████████████████████████| 5/5 Complete
2022-09-02 17:29:07,611 [INFO] Downloading log-events
Progress: |██████████████████████████████████████████████████| 65/65 Complete
2022-09-02 17:29:07,827 [INFO] Downloading log-metric-v2
2022-09-02 17:29:07,968 [INFO] Downloading os-services-monitoring-old
Progress: |██████████████████████████████████████████████████| 32/32 Complete
2022-09-02 17:29:08,690 [INFO] Downloading os-services-monitoring
Progress: |██████████████████████████████████████████████████| 2/2 Complete


```
```
python3 .\main.py --log-level DEBUG --log-path .\logs\ -e TEST --config config.ini --download ./download-location 
```