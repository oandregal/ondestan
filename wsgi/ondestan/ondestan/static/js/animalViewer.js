(function(NS) {

	var google_layer;
	var osm_layer;
	var animals_layer;
	var plots;
    var map;
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
    };

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
    };

    function addToPopover(feature){
        var device = feature.properties;
        var zoomString = '<span class="glyphicon glyphicon-search"></span> ';
        if (feature.geometry){
            var lng = feature.geometry.coordinates[0];
            var lat = feature.geometry.coordinates[1];
            zoomString = '<a href="#" onclick="window.OE.zoom('+lng+','+lat+')"><span class="glyphicon glyphicon-screenshot" disabled></span>  </a>';
        }
        var name = device.name || device.imei;
        var battery = device.battery || batteryStandards.level.noData;
        var url = contextVariables.deactivate_device_url.replace('__device_id__', device.id);
        var toggleClass = 'toggle_' + device.id;
        var activation = contextVariables.deactivate_device_msg;
        if(!device.active){
            url = contextVariables.activate_device_url.replace('__device_id__', device.id);
            activation = contextVariables.activate_device_msg;
            zoomString = '<span class="glyphicon glyphicon-search"></span> ';
            battery = batteryStandards.level.noData;
        }
        return '<li class="list-group-item">' +
        	'<form role="form" class="form-inline" action="' + contextVariables.update_animal_name_url + '" method="post">' +
            '<input type="hidden" id="id" name="id" style="display: none;" value="' + device.id + '"/>' +
            '<a href="' + url + '" type="button" class="pull-right btn btn-default btn-xs">' + activation + '</a>' +
            zoomString +
            '<input class="form-control '+toggleClass+'" type="text" id="name" style="display: none;" name="name" value="' + (device.name || '') + '" />' +
            '<label data-toggle="tooltip" data-placement="top" title="' + window.contextVariables.edit_name_tooltip + '" class="'+toggleClass+'" ondblclick="$(\'.'+toggleClass+'\').toggle(0)">' + name + '</label>'+
            '<span class="badge">' + battery + '%</span>' +
            '</form>' +
            '</li>';
    }

    NS.zoom = function(lng, lat){
        var offset = 0.002;
        var southWest = L.latLng(lat-offset, lng-offset),
        northEast = L.latLng(lat+offset, lng+offset),
        bounds = L.latLngBounds(southWest, northEast);
        map.fitBounds(bounds);
    };

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

    NS.init = function(){
    	map = L.map('map', {zoomControl: false});
    	zoom = L.control.zoom({zoomInTitle: window.contextVariables.zoom_in_tooltip, zoomOutTitle: window.contextVariables.zoom_out_tooltip});
    	map.addControl(zoom);
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

        load_plots();
        load_animals();

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

		map.addControl(displayLegendControl(DisplayLegendFunction));
		
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
        NS.init();
    });

})(window.OE = window.OE || {});
