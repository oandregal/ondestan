var user_position = null;
var google_layer;
var osm_layer;
var map;

function zoom(lng, lat) {
    var offset = 0.002;
    var southWest = L.latLng(lat-offset, lng-offset),
    northEast = L.latLng(lat+offset, lng+offset),
    bounds = L.latLngBounds(southWest, northEast);
    map.fitBounds(bounds);
}

function checkBaseLayer() {
	if (map.getZoom() > 15) {
		if (!map.hasLayer(google_layer)) {
			map.removeLayer(osm_layer);
			map.addLayer(google_layer);
		}
	} else {
		if (!map.hasLayer(osm_layer)) {
			map.removeLayer(google_layer);
			map.addLayer(osm_layer);
		}
	}
}

function init(){
	map = L.map(window.contextVariables.map_widget_id, {zoomControl: false});
	zoomControl = L.control.zoom({zoomInTitle: window.contextVariables.zoom_in_tooltip, zoomOutTitle: window.contextVariables.zoom_out_tooltip});
	map.addControl(zoomControl);
	if (window.contextVariables.map_view_json != null) {
    	if (window.contextVariables.map_view_json.type == 'Polygon') {
    		points = []
    		for (i in window.contextVariables.map_view_json.coordinates[0]) {
    			points.push([window.contextVariables.map_view_json.coordinates[0][i][1], window.contextVariables.map_view_json.coordinates[0][i][0]]);
    		}
    		map.fitBounds(points);
    	} else {
    		point = [window.contextVariables.map_view_json.coordinates[1], window.contextVariables.map_view_json.coordinates[0]]
    		map.setView(point, 13);
    	}
	} else {
		map.setView(window.contextVariables.default_view, 8);
	}

	load_data();
	
	controls = additionalControls();
	for (i = 0, len = controls.length; i < len; i++) {
		map.addControl(controls[i]);
	}
	
	google_layer = new L.Google('SATELLITE');
    osm_layer = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '<a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
    })

    checkBaseLayer();
    map.on('zoomend', function() {
    	checkBaseLayer();
    });
};

// Init on document ready
$(function(){
    init();
});
