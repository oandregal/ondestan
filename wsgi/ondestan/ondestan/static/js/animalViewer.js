var animals_layer;
var animal_approx_pos_layer;
var plots;
var active_devices;
var active_devices_popover_content;
var inactive_devices;
var inactive_devices_popover_content;
var low_battery_devices;
var low_battery_devices_popover_content;
var outside_plots_devices;
var outside_plots_devices_popover_content;
var batteryStandards = {
    level: {
        low: window.contextVariables.low_battery_barrier,
        middle: window.contextVariables.medium_battery_barrier,
        noData: '---',
    },
    color: {
        high:     "#a1d99b", // green, kindof
        middle:   "#feb24c",  // orange, kindof
        low:      "#de2d26", // red, kindof
        inactive: "#bdbdbd", // grey, kindof
    },
    opacity:{
        active: 1,
        inactive: 0.7,
    }
};

function getStyleForDevice(feature){
    var device = feature.properties;
    var opt = {
        stroke: false,
        radius: 8,
        fillColor: batteryStandards.color.high,
        fillOpacity: batteryStandards.opacity.active,
        opacity: 1,
        color: "black",
        weight: 3
    };

    if(!device.active){
        opt.fillColor = batteryStandards.color.inactive;
        opt.fillOpacity = batteryStandards.opacity.inactive;
    } else if (device.battery < batteryStandards.level.low) {
        opt.fillColor = batteryStandards.color.low;
    } else if (device.battery < batteryStandards.level.middle) {
        opt.fillColor = batteryStandards.color.middle;
    }
    if (device.outside) {
    	opt.stroke = true;
    }
    return opt;
}

function show_current_approx_position(animal_id) {
	if (animal_approx_pos_layer != null) {
		map.removeLayer(animal_approx_pos_layer);
	}
	animal_approx_pos_layer = new L.FeatureGroup();
	animal_approx_pos_data = new L.GeoJSON.AJAX(contextVariables.animal_approx_position_json_url.replace('__animal_id__', animal_id),{
	    style: function (feature) {
	    	return {color: "#FFF700", fillOpacity: 0.3, weight: 0};
	    },
        onEachFeature: function (feature, layer) {
        	layer.bindPopup(feature.properties.popup);
        	animal_approx_pos_layer.addLayer(layer);
        },
        middleware: function(data) {
        	if (data.length == 0) {
        		$('#no-info-app-position-modal').modal();
        	}
        	return data;
        }
    });

	animal_approx_pos_data.on('data:loaded', function(e) {
		animal_approx_pos_layer.bringToBack();
		map.fitBounds(animal_approx_pos_layer.getBounds());
	});

	map.addLayer(animal_approx_pos_layer);
}

function addToPopover(feature){
    var device = feature.properties;
    var zoomString = '<span class="glyphicon glyphicon-screenshot" disabled></span> ';
    var historyString = '<span class="history-link glyphicon glyphicon-calendar pull-right" disabled></span> ';
    var approxPositionString = '<span class="glyphicon glyphicon-hand-down" disabled></span>';
    if (feature.geometry){
        var lng = feature.geometry.coordinates[0];
        var lat = feature.geometry.coordinates[1];
        zoomString = '<a data-toggle="tooltip" data-placement="top" title="' + window.contextVariables.center_view_on_animal_tooltip + '"' +
        	' href="#" onclick="zoom('+lng+','+lat+')"><span class="glyphicon glyphicon-screenshot"></span>  </a>';
        historyString = '<a href="' + window.contextVariables.positions_history_url + device.id + '"><span data-toggle="tooltip" data-placement="top" title="' +
        	window.contextVariables.view_positions_history_tooltip + '" class="history-link glyphicon glyphicon-calendar pull-right"></span>  </a>';
        approxPositionString = '<a data-toggle="tooltip" data-placement="top" title="' + window.contextVariables.show_animal_current_approx_position_tooltip + '"' +
        ' href="#" onclick="show_current_approx_position(' + device.id + ')"><span class="glyphicon glyphicon-hand-down"></span>  </a>';
    }
    var name = device.name || device.imei;
    var battery = device.battery || batteryStandards.level.noData;
    var url = contextVariables.deactivate_device_url.replace('__device_id__', device.id);
    var toggleClass = 'toggle_' + device.id;
    var activation = contextVariables.deactivate_device_msg;
    if (!device.active){
        url = contextVariables.activate_device_url.replace('__device_id__', device.id);
        activation = contextVariables.activate_device_msg;
        battery = batteryStandards.level.noData;
    }
    return '<li class="list-group-item">' +
    	'<form role="form" class="form-inline" action="' + contextVariables.update_animal_name_url + '" method="post">' +
        '<input type="hidden" id="id" name="id" style="display: none;" value="' + device.id + '"/>' +
        '<a href="' + url + '" type="button" class="pull-right btn btn-default btn-xs">' + activation + '</a>' +
        zoomString +
        approxPositionString +
        '<input class="form-control '+toggleClass+'" type="text" id="name" style="display: none;" name="name" value="' + (device.name || '') + '" />' +
        '<label data-toggle="tooltip" data-placement="top" title="' + window.contextVariables.edit_name_tooltip + '" class="'+toggleClass+'" ondblclick="$(\'.'+toggleClass+'\').toggle(0)">' + name + '</label>'+
        '<span class="badge">' + battery + '%</span>' +
        historyString +
        '</form>' +
        '</li>';
}

function load_plots() {
	plots = new L.FeatureGroup();
	new L.GeoJSON.AJAX(contextVariables.plots_json_url,{
//		    style: function (feature) {
//		        return {clickable: false};
//		    },
        onEachFeature: function (feature, layer) {
        	if (feature.properties.popup != null && feature.properties.popup != '') {
        		layer.bindPopup(feature.properties.popup);
        	}
        	plots.addLayer(layer);
        }
    });

	map.addLayer(plots);
}

function load_animals() {
    active_devices = [];
    active_devices_popover_content = '';
    inactive_devices = [];
    inactive_devices_popover_content = '';
    low_battery_devices = [];
    low_battery_devices_popover_content = '';
    outside_plots_devices = [];
    outside_plots_devices_popover_content = '';

	animals_layer = new L.GeoJSON.AJAX(contextVariables.animals_json_url,{
        pointToLayer: function (feature, latlng) {
            return new L.CircleMarker(latlng, getStyleForDevice(feature));
        },
        middleware: function(data) {
            for (i = 0, len = data.length; i < len; i++) {
                var device = data[i].properties;
                if (device.active) {
                    if ((device.battery != null) && (device.battery < batteryStandards.level.low)) {
                        low_battery_devices.push(data[i]);
                        low_battery_devices_popover_content += addToPopover(data[i]);
                    }
                    if (device.outside) {
                        outside_plots_devices.push(data[i]);
                        outside_plots_devices_popover_content += addToPopover(data[i]);
                    }
                    active_devices.push(data[i]);
                    active_devices_popover_content += addToPopover(data[i]);
                } else {
                    inactive_devices.push(data[i]);
                    inactive_devices_popover_content += addToPopover(data[i]);
                }
            }
            return data;
        },
        onEachFeature: function (feature, layer) {
            layer.bindPopup(feature.properties.popup);
        }
    });

	animals_layer.on('data:loaded', function(e) {

        $('#active_devices').text(active_devices.length);
        if (active_devices_popover_content != '') {
            $('#active_devices').removeAttr('disabled');
            $('#active_devices').popover({
                html: true,
                placement: 'bottom',
                trigger: 'click',
                content: '<ul id="active_devices_popover_content" class="list-group">' + active_devices_popover_content + '</ul>',
            });
            $('#active_devices').on('shown.bs.popover', function () {
                $( "#active_devices_popover_content [data-toggle='tooltip']" ).tooltip({delay: {show: 750, hide: 0}});
            })
        }

        $('#inactive_devices').text(inactive_devices.length);
        if (inactive_devices_popover_content != '') {
            $('#inactive_devices').removeAttr('disabled');
            $('#inactive_devices').popover({
                html: true,
                placement: 'bottom',
                trigger: 'click',
                content: '<ul id="inactive_devices_popover_content" class="list-unstyled">' + inactive_devices_popover_content + '</ul>',
            });
            $('#inactive_devices').on('shown.bs.popover', function () {
                $( "#inactive_devices_popover_content [data-toggle='tooltip']" ).tooltip({delay: {show: 750, hide: 0}});
            })
        }

        if (low_battery_devices.length > 0) {
        	$('#low_battery_devices').addClass('devices-alert');
        }
        $('#low_battery_devices').text(low_battery_devices.length);
        if (low_battery_devices_popover_content != '') {
            $('#low_battery_devices').removeAttr('disabled');
            $('#low_battery_devices').popover({
                html: true,
                placement: 'bottom',
                trigger: 'click',
                content: '<ul id="low_battery_devices_popover_content" class="list-unstyled">' + low_battery_devices_popover_content + '</ul>',
            });
            $('#low_battery_devices').on('shown.bs.popover', function () {
                $( "#low_battery_devices_popover_content [data-toggle='tooltip']" ).tooltip({delay: {show: 750, hide: 0}});
            })
        }

        if (outside_plots_devices.length > 0) {
        	$('#outside_plots_devices').addClass('devices-alert');
        }
        $('#outside_plots_devices').text(outside_plots_devices.length);
        if (outside_plots_devices_popover_content != '') {
            $('#outside_plots_devices').removeAttr('disabled');
            $('#outside_plots_devices').popover({
                html: true,
                placement: 'bottom',
                trigger: 'click',
                content: '<ul id="outside_plots_devices_popover_content" class="list-unstyled">' + outside_plots_devices_popover_content + '</ul>',
            });
            $('#outside_plots_devices').on('shown.bs.popover', function () {
                $( "#outside_plots_devices_popover_content [data-toggle='tooltip']" ).tooltip({delay: {show: 750, hide: 0}});
            })
        }

    });

	animals_layer.addTo(map);
}

function load_data() {
    load_plots();
    load_animals();
}

function additionalControls() {
	controls = []

	displayLegendControl = function(theDisplayLegendFunction) {

	    var control = new (L.Control.extend({
	    options: { position: 'topright' },
	    onAdd: function (map) {
	        controlDiv = L.DomUtil.create('div', 'display-legend-button');
	        L.DomEvent
	            .addListener(controlDiv, 'click', L.DomEvent.stopPropagation)
	            .addListener(controlDiv, 'click', L.DomEvent.preventDefault)
	            .addListener(controlDiv, 'click', this.DisplayLegendFunction);

	        // Set CSS for the control border
	        var controlUI = L.DomUtil.create('div', 'display-legend-toolbar leaflet-bar display-legend-toolbar-top', controlDiv);
	        controlUI.title = window.contextVariables.show_map_legend_tooltip;

	        // Set CSS for the control interior
	        var controlText = L.DomUtil.create('a', 'leaflet-div-icon leaflet-control-zoom-in', controlUI);
	        controlText.href = '#';
	        controlText.innerHTML = '?';

	        return controlDiv;
	    }
	    }));

	    control.DisplayLegendFunction = theDisplayLegendFunction;

	    return control;
	};

	DisplayLegendFunction = function () { $('#legend-modal').modal();};

	controls.push(displayLegendControl(DisplayLegendFunction));
	
	return controls;
}
