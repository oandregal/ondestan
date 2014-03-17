$( function() {
	var map = L.map('map').setView([51.505, -0.09], 13);

	function load_cows() {
		new L.GeoJSON.AJAX(contextVariables.application_url + "/json/cows.json",{
			pointToLayer: function (feature, latlng) { 
				var color = "green"; 
				var weight = 0; 
	            if (feature.properties.battery_level < 20.0) {
	            	color = "red";
	            } else {
		            if (feature.properties.battery_level < 50.0) {
		            	color = "yellow";
		            }
	            }
	            if (feature.properties.outside) {
	            	weight = 5;
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
		}).addTo(map);
	}

	new L.GeoJSON.AJAX(contextVariables.application_url + "/json/plots.json",{
        onEachFeature: function (feature, layer) {
            layer.bindPopup(feature.properties.popup);
        },
        middleware:function(data){
            load_cows();
            return data;
        }
	}).addTo(map);

	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		maxZoom: 18,
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>'
	}).addTo(map);
});