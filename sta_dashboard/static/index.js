document.addEventListener('DOMContentLoaded', function () {
    
    document.querySelector('#endpoints-checkbox').onsubmit = function () {

        // Initialize new request
        const request = new XMLHttpRequest();
        var endpoints_list = document.querySelectorAll('input[name=endpoint]:checked');
        request.open('POST', '/show_points');

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

                var popUpContent = [];
                for (var i = 0; i < row.datastreams.length; i++) {

                    var a = document.createElement('a'); // Create anchor for link to datastreams
                    var datastreams_text = document.createTextNode(row.datastreams[i]['name']);
                    a.appendChild(datastreams_text);
                    a.href = row[2][i]['@iot.selfLink'];
                    a.target = '_blank';

                    popUpContent.push(a.outerHTML)
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
