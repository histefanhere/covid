#/bin/bash

# A dead simple script to download the latest stats for the latest covid cases.
# Expected to be executed periodically as a cronjob - see `crontab.example` for an example configuration.

cd "$(dirname "$0")"
curl https://www.health.govt.nz/covid-19-novel-coronavirus/covid-19-data-and-statistics/covid-19-current-cases -o covid-19-current-cases.html
