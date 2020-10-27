# sta-dashboard
A SensorThings API dashboard

My goal is an easy-to-deploy and use web application that basically has the same functionality as this: https://gemstat.bafg.de/applications/public.html?publicuser=PublicUser
 
Eg., there is a web map showing locations of all stations. Stations are filterable by what parameters they have data on. When you click a station, you can select which parameters you are interested in, and visualize the results as tabular data or a line graph. You can also choose to export data form all selected parameters and stations as a CSV file. This should be able to run against any SensorThings API endpoint. Some example endpoints are here:
 
https://sta-demo.internetofwater.dev/api/v1.1
https://sta.ci.taiwan.gov.tw/STA_AirQuality_EPAIoT/v1.1
https://st.newmexicowaterdata.org/FROST-Server/v1.1
https://service.datacove.eu/AirThings/v1.1/
 
Ideally, the dashboard would be able to consume from multiple endpoints, that the user could specify, or could be configured without allowing the end user to specify.
 
This is the official documentation for the API http://docs.opengeospatial.org/is/15-078r6/15-078r6.html
This is some good interactive documentation for the API, focus on the GET requests https://gost1.docs.apiary.io/#

# Dependencies
- requirements.txt

# Storyboard
## [ ] Add a backend database
1. [ ] SQLite3 for development; PostgreSQL for deployment
2. [ ] Download data from API endpoints and update regularly
## [x] Show location points on a map
1. [x] Use OSM tiles and leaflet.js
2. [x] Test on multiple endpoints
3. [ ] Cluster markers at lower zoom levels
4. [?] Potential issue: slow loading when the number of points goes above thousands/tens of thousands.
## [ ] Show location in tabular
## [ ] Filter points on the map by their propterties
1. [ ] Select filterable & supported features
## [ ] Show information of each point
1. [ ] Show summaries of key features at hover
2. [ ] Show a dialog box at click that supports
    1. [ ] Feature visualization (tabular, scatter plot, line chart)
    2. [ ] Export as CSV
## [ ] Docker containerization
