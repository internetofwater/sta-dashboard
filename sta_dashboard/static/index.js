document.addEventListener('DOMContentLoaded', function () {
    
    document.querySelector('#endpoints-checkbox').onsubmit = function () {

        // Initialize new request
        const request = new XMLHttpRequest();
        var endpoints_list = document.querySelectorAll('input[name=endpoint]:checked');
        request.open('POST', '/show_points');

        request.onload = function () {

            var data = JSON.parse(request.responseText);

            map.flyTo([data.locations[0][0], data.locations[0][1]], data.zoom_level);


            // Create a new MarkerClusterGroup
            var markers = L.markerClusterGroup({
                spiderfyOnMaxZoom: false,
                chunkedLoading: true,
                maxZoom: 12
            });

            // Add point markers
            var markerList = [];

            for (row of data.locations) {
                var marker = L.marker([row[0], row[1]]);

                var popUpContent = [];
                for (var i = 0; i < row[2].length; i++) {
                    var datastreams_name = row[2][i]['name'];
                    var datastreams_selfLink = datastreams_name.link(row[2][i]['@iot.selfLink']);
                    popUpContent.push(datastreams_selfLink)
                }

                marker.bindPopup(`Datastreams: ${popUpContent.join(', ')}`);
                markerList.push(marker);
            };

            markers.addLayers(markerList);
            map.addLayer(markers);

            const checckbox_title = `${markerList.length} locations found.`;
            document.querySelector('#checkbox-title').innerHTML = checckbox_title;

        }

        var data = [];
        for (endpoint of endpoints_list) {
            data.push(endpoint.value)
        };

        const dataStr = new FormData();
        dataStr.append('endpoints', JSON.stringify(data));

        // Send the endpoints list to server
        request.send(dataStr);
        return false;

    }
})
