# sta-dashboard
A SensorThings API dashboard

My goal is an easy-to-deploy and use web application that basically has the same functionality as this: https://gemstat.bafg.de/applications/public.html?publicuser=PublicUser
 
Eg., there is a web map showing locations of all stations. Stations are filterable by what parameters they have data on. When you click a station, you can select which parameters you are interested in, and visualize the results as tabular data or a line graph. You can also choose to export data form all selected parameters and stations as a CSV file. This should be able to run against any SensorThings API endpoint. Some example endpoints are here:
 
* https://sta-demo.internetofwater.dev/api/v1.1
* https://sta.ci.taiwan.gov.tw/STA_AirQuality_EPAIoT/v1.1
* https://st.newmexicowaterdata.org/FROST-Server/v1.1
* https://service.datacove.eu/AirThings/v1.1/
 
Ideally, the dashboard would be able to consume from multiple endpoints, that the user could specify, or could be configured without allowing the end user to specify.
 
This is the official documentation for the API http://docs.opengeospatial.org/is/15-078r6/15-078r6.html
This is some good interactive documentation for the API, focus on the GET requests https://gost1.docs.apiary.io/#

# Usage
## Select which endpoints to include:
### Option 1: Start from scratch
- Edit endpoints to include in `endpoints.json`.

### Option 2: Load a external pre-cached database
- Edit environment variables `SQLITE_DB_FILENAME` in `.env` file. The actual SQLite databse file should be place under `sta_dashboard/data/`. **Loading pre-cached database will overwrite settings in `endpoints.json`.**

With either option, run `docker-compose up` to start the application. The web app will be running on `localhost:${FLASK_HOST_PORT}` on your host machine.

## Apply changes to `endpoints.json` or pre-cached db when the app is running:
- Save all changes.
    - If not loading a pre-cached databse, assign a different filename for `SQLITE_DB_FILENAME` in `.env` as the previous filename was used to create a cached database file.
- Run `docker-compose build`.
- RUn `docker-compose up`.

# Dependencies
- [See requirements.txt](requirements.txt)

# Storyboard
## [x] Cached database
1. [x] Supports SQLAlchemy supported databases (e.g. PostgreSQL and SQLite).
## [x] Show location points on a map
1. [x] Display OSM tiles with leaflet.js
2. [x] Support selecting multiple endpoints
3. [x] Cluster markers at lower zoom levels
4. [x] Potential issue: slow loading when the number of points goes above thousands/tens of thousands.
    - Solved: Support persistent docker volumes and loading from external pre-cached db.

## [x] Filter points to display on the map by observed properties
## [ ] Show detailed information for each point
1. [ ] Show summaries of key features on hover
2. [x] Show on click:
    1. [x] Feature visualization (connected time series plot, supports pan&zoom)
    2. [x] Export as CSV
    3. [x] Show links to datastreams when hover on datastream names
## [ ] Docker containerization
1. [x] Add docker-compose file to configure containers for web app and PostgreSQL database
