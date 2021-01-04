document.addEventListener('DOMContentLoaded', function () {

    var loader = document.getElementById('modal');
    
    document.querySelector('#query-filters').onsubmit = function () {

        loader.style.display = "block";

        // Initialize new request
        const request = new XMLHttpRequest();
        var endpoints_list = document.querySelectorAll('input[name="endpoint"]:checked');
        var start_date = document.querySelector('input[name="start-date"]');
        var end_date = document.querySelector('input[name="end-date"]');

        if (start_date.value.length > 0 && end_date.value.length > 0) {
            if (start_date.value >= end_date.value) {
                window.alert('Invalid date range: end date must be after start date');
                window.stop();
            }
        }

        request.open('POST', '/query_points');

        request.onload = function () {

            var data = JSON.parse(request.responseText);

            map.eachLayer(function (layer) {
                if (layer['options']['id'] != 'tileLayer') {
                    layer.remove()
                }
            });

            map.flyTo(data.viewLatlon, data.zoom_level);


            // Create a new MarkerClusterGroup
            var markers = L.markerClusterGroup({
                spiderfyOnMaxZoom: false,
                chunkedLoading: true,
                maxZoom: 12
            });

            // Add point markers
            var markerList = [];

            for (row of data.locations) {
                var marker = L.marker([row.latitude, row.longitude]);

                // TODO: Remove duplicate locations/group datastreams by locations
                var popUpContent = [];
                for (var i = 0; i < row.length; i++) {
                    var a = document.createElement('a'); // Create anchor for link to datastreams
                    var datastreams_text = document.createTextNode(row.datastreams.name[i]);
                    a.appendChild(datastreams_text);
                    a.href = row.datastreams.selfLink[i];
                    a.target = '_blank';
                    popUpContent.push(a.outerHTML);
                };
                marker.bindPopup(`Datastreams: ${popUpContent.join(', ')}`)
                markerList.push(marker);
            };

            markers.addLayers(markerList);
            map.addLayer(markers);

            const checckbox_title = `${markerList.length} locations found.`;
            document.querySelector('#checkbox-title').innerHTML = checckbox_title;
            loader.style.display = 'none';
            window.alert(checckbox_title);

        }

        var endpoints = [];
        for (endpoint of endpoints_list) {
            endpoints.push(endpoint.value)
        };

        const dataStr = new FormData();
        dataStr.append('endpoints', JSON.stringify(endpoints));
        dataStr.append('startDate', JSON.stringify(start_date.value));
        dataStr.append('endDate', JSON.stringify(end_date.value));

        // Send the endpoints list to server
        request.send(dataStr);
        return false;

    }
})
