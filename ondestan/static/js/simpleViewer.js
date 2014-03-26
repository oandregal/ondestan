$( function() {
	var map = L.map('map').setView([42.25, -7.54], 13);
	var active_devices = [];
	var low_battery_devices = [];

	function load_cows() {
		layer = new L.GeoJSON.AJAX(contextVariables.animals_json_url,{
			pointToLayer: function (feature, latlng) {
				var color = "green";
				var weight = 0;
				active_devices.push(feature);
	            if (feature.properties.battery < 20.0) {
	            	color = "red";
	            	low_battery_devices.push(feature);
	            } else {
		            if (feature.properties.battery < 50.0) {
		            	color = "yellow";
		            }
	            }
	            if (feature.properties.outside) {
	            	weight = 2;
	            }
                return new L.CircleMarker(latlng, {
                    radius: 8,
                    fillColor: color,
                    color: "black",
                    weight: weight,
                    opacity: 1,
                    fillOpacity: 1
                });
            },
            onEachFeature: function (feature, layer) {
                layer.bindPopup(feature.properties.popup);
	        }
		});
		layer.on('data:loaded', function(e) {
			$('#low_battery_devices').text(low_battery_devices.length);
			$('#active_devices').text(active_devices.length);
		});
		layer.addTo(map);
	}

	new L.GeoJSON.AJAX(contextVariables.plots_json_url,{
        onEachFeature: function (feature, layer) {
            layer.bindPopup(feature.properties.popup);
        },
        middleware:function(data){
            load_cows();
            return data;
        }
	}).addTo(map);

        L.tileLayer('http://a.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	    maxZoom: 18,
	    attribution: '<a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
        }).addTo(map);

});
