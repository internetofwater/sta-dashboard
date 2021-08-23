document.addEventListener('DOMContentLoaded', function () {

    var loader = document.getElementById('map-loader');
    
    document.querySelector('#query-filters').onsubmit = function () {

        loader.style.display = "block";

        // Initialize new request
        const query_request = new XMLHttpRequest();
        const ds_request = new XMLHttpRequest();
        const visualize_request = new XMLHttpRequest();
        const downloadCsv_request = new XMLHttpRequest();

        var properties_list = document.querySelectorAll('input[name="prop"]:checked');
        var start_date = document.querySelector('input[name="start-date"]');
        var end_date = document.querySelector('input[name="end-date"]');

        if (start_date.value.length > 0 && end_date.value.length > 0) {
            if (start_date.value >= end_date.value) {
                window.alert('Invalid date range: end date must be after start date');
                window.stop();
            }
        }

        query_request.open('POST', '/query_points');
        query_request.onload = function () {

            var data = JSON.parse(query_request.responseText);

            map.eachLayer(function (layer) {
                if (layer['options']['id'] != 'tileLayer') {
                    layer.remove()
                }
            });

            map.flyTo(data.viewLatlon, data.zoom_level);

            // Create a new MarkerClusterGroup for point locations
            const markers = L.markerClusterGroup({
                spiderfyOnMaxZoom: false,
                chunkedLoading: true,
                maxZoom: 12
            });

            // Create a new Deflate for polygon locations
            const polygons = L.deflate({
                minSize: 100,
                markerLayer: markers
            });
            
            var featureList = [];

            for (row of data.locations) {
                var geojsonFeature = {
                    "type": "Feature",
                    "geometry": row.location_geojson
                };
                var feature = L.geoJSON(geojsonFeature, {title: row.thingId}).on('click', featureOnClick);

                function featureOnClick(e) {
                    var thingId = e.target.options.title

                    var chartModal = document.getElementById('visualizationModal');
                    var span = document.getElementsByClassName("close")[0];
                    var canvasDiv = document.getElementById('canvasDiv');
                    canvasDiv.style.display = 'none';
                    var dsSelectorDiv = document.getElementById('datastreamsSelectorDiv');
                    dsSelectorDiv.innerHTML = '';


                    ds_request.open('POST', '/show_available_datastreams');

                    const dsDataStr = new FormData();
                    dsDataStr.append('thingId', JSON.stringify(thingId));
                    ds_request.send(dsDataStr);
                    ds_request.onload = function () {

                        var dsData = JSON.parse(ds_request.responseText);

                        for (i = 0; i < dsData.availableDatastreamsByProperty.length; i++) {

                            // Populate available datastreams and make a checkbox for each
                            var dsName = dsData.availableDatastreamsByProperty[i];
                            var dsId = dsData.availableDatastreamsById[i];
                            var dsLink = dsData.availableDatastreamsByLink[i];

                            var el = document.createElement('input');
                            var label = document.createElement('label');
                            el.type = 'checkbox';
                            el.name = 'datastream_available';
                            el.value = dsId;
                            dsSelectorDiv.appendChild(el);
                            dsSelectorDiv.appendChild(label);

                            var tooltipText = document.createElement('span');
                            tooltipText.classList.add('tooltiptext');
                            var tooltipTextLink = document.createElement('a');
                            tooltipTextLink.href = dsLink;
                            tooltipTextLink.target = '_blank';
                            tooltipTextLink.innerHTML = 'Link to datastream';
                            
                            tooltipText.appendChild(tooltipTextLink);
                            label.appendChild(tooltipText);
                            label.classList.add('tooltip');
                            label.appendChild(document.createTextNode(dsName));

                        }

                        linebreak = document.createElement('br');
                        dsSelectorDiv.appendChild(linebreak);

                        submitButton = document.createElement('input')
                        submitButton.type = 'button';
                        submitButton.value = 'Visualize';
                        dsSelectorDiv.appendChild(submitButton);

                        submitButton.onclick = function () {

                            canvasDiv.innerHTML = '';
                            visualize_request.open('POST', '/visualize_observations');

                            // Construct a form of data to send to server
                            const visualizeDataStr = new FormData();
                            var ds_list = document.querySelectorAll('input[name="datastream_available"]:checked');
                            var dsListValues = new Array();
                            for (var ds of ds_list.values()) {
                                dsListValues.push(ds.value);
                            }

                            visualizeDataStr.append('startDate', JSON.stringify(start_date.value));
                            visualizeDataStr.append('endDate', JSON.stringify(end_date.value));
                            visualizeDataStr.append('thingId', JSON.stringify(thingId));
                            visualizeDataStr.append('dsList', JSON.stringify(dsListValues));

                            // Plot the data with chart.js
                            visualize_request.onload = function () {
                                var observations = JSON.parse(visualize_request.responseText);
                                var canvasEl = document.createElement('canvas');
                                canvasEl.maintainAspectRatio = false;
                                canvasDiv.appendChild(canvasEl);

                                var scatterChart = new Chart(canvasEl, {
                                    type: 'scatter',
                                    data: {
                                        datasets: observations['value']
                                    },
                                    options: {
                                        scales: {
                                            xAxes: [{
                                                ticks: {
                                                    autoSkip: true,
                                                    maxTicksLimit: 10
                                                },
                                                type: 'time',
                                                time: {
                                                    parser: 'X',
                                                    tooltipFormat: "h:mm a MM/DD/YY",
                                                    displayFormats: {
                                                        day: 'MMM D YYYY',
                                                        month: 'MMM D YYYY',
                                                        year: 'MMM D YYYY',
                                                        hour: 'h:mm a MM/DD/YY',
                                                        minute: 'h:mm a MM/DD/YY'
                                                    }
                                                }
                                            }]
                                        },
                                        plugins: {
                                            colorschemes: {
                                                scheme: 'tableau.Classic20'
                                            },
                                            zoom: {
                                                pan: {
                                                    enabled: true,
                                                    mode: 'xy'
                                                },
                                                zoom: {
                                                    enabled: true,
                                                    mode: 'xy'
                                                }
                                            }
                                        },
                                    }
                                });
                                canvasDiv.style.display = 'block';
                            }

                            visualize_request.send(visualizeDataStr);
                        }

                        downloadCsvButton = document.createElement('input')
                        downloadCsvButton.type = 'button';
                        downloadCsvButton.value = 'Download as CSV';
                        dsSelectorDiv.appendChild(downloadCsvButton);

                        downloadCsvButton.onclick = function () {
                            downloadCsv_request.open('POST', '/download_observations');
                            downloadCsv_request.responseType = 'blob';

                            // Construct a form of data to send to server
                            const downloadCsvDataStr = new FormData();
                            var ds_list = document.querySelectorAll('input[name="datastream_available"]:checked');
                            var dsListValues = new Array();
                            for (var ds of ds_list.values()) {
                                dsListValues.push(ds.value);
                            }

                            downloadCsvDataStr.append('startDate', JSON.stringify(start_date.value));
                            downloadCsvDataStr.append('endDate', JSON.stringify(end_date.value));
                            downloadCsvDataStr.append('thingId', JSON.stringify(thingId));
                            downloadCsvDataStr.append('dsList', JSON.stringify(dsListValues));

                            downloadCsv_request.onload = function (e) {
                                var blob = e.currentTarget.response;
                                var contentDispo = e.currentTarget.getResponseHeader('Content-Disposition');
                                var fileName = contentDispo.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)[1];
                                saveBlob(blob, fileName);

                                function saveBlob(blob, fileName) {
                                    var a = document.createElement('a');
                                    a.href = window.URL.createObjectURL(blob);
                                    a.download = fileName;
                                    a.dispatchEvent(new MouseEvent('click'));
                                }
                            }

                            downloadCsv_request.send(downloadCsvDataStr);
                        }

                    }

                    chartModal.style.display = 'block';
                    span.onclick = function () {
                        canvasDiv.innerHTML = '';
                        chartModal.style.display = "none";
                    }
                }

                if (geojsonFeature.geometry.type == 'Point') {
                    feature.addTo(markers)
                } else if (geojsonFeature.geometry.type == 'MultiPolygon' || geojsonFeature.geometry.type == 'Polygon') {
                    feature.addTo(polygons)
                }

                featureList.push(feature);

            }

            map.addLayer(markers);
            map.addLayer(polygons);

            const checckbox_title = `${featureList.length} locations found.`;
            document.querySelector('#checkbox-title').innerHTML = checckbox_title;
            loader.style.display = 'none';
            window.alert(checckbox_title);

        }

        var endpoints = [];
        var properties = [];
        for (property of properties_list) {
            [endpoint, prop] = property.value.split(',');
            properties.push(prop);
            endpoints.push(endpoint);
        }

        const dataStr = new FormData();
        dataStr.append('endpoints', JSON.stringify(endpoints));
        dataStr.append('properties', JSON.stringify(properties));
        dataStr.append('startDate', JSON.stringify(start_date.value));
        dataStr.append('endDate', JSON.stringify(end_date.value));

        // Send the endpoints list to server
        query_request.send(dataStr);
        return false;

    }
})
