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

## First-time use
1. Edit `endpoints.json` to select which endpoints to be included in the application. **No space allowed in endpoint keys.**
2. Edit `.env` environment variables:
    - **SQLITE_DB_FILENAME (type:str)**: Filename for the cached database. If there's a pre-cached SQLite3 database file, put the file under `sta_dashboard/data` and the application will read from the cached SQLite3 database. Otherwise, the application will create a new SQLite3 database saved by this filename.
    - **DROP_ALL (type:bool)**: If drop all existing cached records and restart caching. Make this `True` to re-cache previously cached records.
    - **FLASK_HOST_PORT (type:int)**: Port number which the Flask web app will be running on.
3. Run `docker-compose up -d` to run the Docker in the background.
4. Access the application at `localhost:<FLASK_HOST_PORT>`

## Make changes to the database for a running application
1. Edit `endpoints.json` and `.env` to make desired changes.
2. Run `docker-compose build` and then `docker-compose up -d`
3. Access the application at `localhost:<FLASK_HOST_PORT>`

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
## [x] Docker containerization
1. [x] Add docker-compose file to configure containers for web app and SQLite3 database
