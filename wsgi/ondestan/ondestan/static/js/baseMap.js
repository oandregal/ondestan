var user_position = null;
var google_layer;
var osm_layer;
var map;

function zoom(lng, lat) {
	$('html, body').animate({
	    scrollTop: ($('#' + window.contextVariables.map_widget_id).offset().top)
	},250);
    var offset = 0.002;
    var southWest = L.latLng(lat-offset, lng-offset),
    northEast = L.latLng(lat+offset, lng+offset),
    bounds = L.latLngBounds(southWest, northEast);
    map.fitBounds(bounds);
}

function centerMapOnPosition(lat, lon) {
	pos = new L.LatLng(lat, lon);
    map.panTo(pos);
    if (map.getZoom() < 12) {
    	map.setZoom(14);
    }
}

function centerMapOnUser(position) {
	if (user_position != null) {
		map.removeLayer(user_position);
	}
	pos = new L.LatLng(position.coords.latitude, position.coords.longitude);
	user_position = new L.marker(pos);
	user_position.addTo(map);
	centerMapOnPosition(position.coords.latitude, position.coords.longitude);
}

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(centerMapOnUser);
    } else { 
        window.alert(window.contextVariables.geolocation_not_supported);
    }
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
		getLocation();
	}

	centerOnUserLocationControl = function(theCenterOnUserFunction) {

	    var control = new (L.Control.extend({
	    options: { position: 'topleft' },
	    onAdd: function (map) {
	        controlDiv = L.DomUtil.create('div', 'display-legend-button');
	        L.DomEvent
	            .addListener(controlDiv, 'click', L.DomEvent.stopPropagation)
	            .addListener(controlDiv, 'click', L.DomEvent.preventDefault)
	            .addListener(controlDiv, 'click', this.CenterOnUserFunction);

	        // Set CSS for the control border
	        var controlUI = L.DomUtil.create('div', 'leaflet-draw-toolbar leaflet-bar leaflet-draw-toolbar-top', controlDiv);
	        controlUI.title = window.contextVariables.center_on_user_position;

	        // Set CSS for the control interior
	        var controlText = L.DomUtil.create('a', 'leaflet-div-icon leaflet-draw-draw-marker', controlUI);
	        controlText.href = '#';

	        return controlDiv;
	    }
	    }));

	    control.CenterOnUserFunction = theCenterOnUserFunction;

	    return control;
	};

	map.addControl(centerOnUserLocationControl(getLocation));

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
