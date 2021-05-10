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
1. Edit endpoints to include in `endpoints.json`
2. Edit environment variables in `.env` file
3. Edit local port to map to from flask container at line 11 in `docker-compose.yml`
# Dependencies
- [See requirements.txt](requirements.txt)

# Storyboard
## [x] Cached database
1. [x] Supports all SQLAlchemy supported databases. Have tested on PostgreSQL and SQLite.
## [x] Show location points on a map
1. [x] Display OSM tiles with leaflet.js
2. [x] Support selecting multiple endpoints
3. [x] Cluster markers at lower zoom levels
4. [ ] Potential issue: slow loading when the number of points goes above thousands/tens of thousands.

## [x] Filter points to display on the map by observed properties
## [ ] Show detailed information for each point
1. [ ] Show summaries of key features on hover
2. [ ] Show on click:
    1. [x] Feature visualization (connected time series plot, supports pan&zoom)
    2. [ ] Export as CSV
    3. [x] Show links to datastreams when hover on datastream names
## [ ] Docker containerization
1. [x] Add docker-compose file to configure containers for web app and PostgreSQL database
2. [ ] Schedule routine updates on cached database in PostgreSQL
