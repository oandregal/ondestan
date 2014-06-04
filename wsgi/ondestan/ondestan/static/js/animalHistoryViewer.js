(function(NS) {

	var ladda;
	var google_layer;
	var osm_layer;
	var timer;
	var interval = 2000;
	var animals_sublayers;
	var animals_features;
	var current_sublayer = null;
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

    
    /**
	* inits slider and a small play/pause button
	*/
	function init_slider() {
		$("#pause").unbind('click');
		// play-pause toggle
		if (animals_sublayers.length >= 1) {
			$("#slider").slider({
				disabled: false,
				min: 0,
				max: animals_sublayers.length - 1,
				value: 0,
				step: 1,
				slide: function(event, ui){
					var step = ui.value;
					load_sublayer(step);
				}
			});
			$("#pause").click(function(){
				clearInterval(timer);
				$(this).toggleClass('playing');
				if ($(this).hasClass('playing')) {
					timer = setInterval(load_next_sublayer, interval);
				}
			});
            if ($('#pause').hasClass('playing')) {
            	timer = setInterval(load_next_sublayer, interval);
            }
		} else {
			if (!$("#pause").hasClass('playing')) {
				clearInterval(timer);
			}
			$("#slider").slider({
				disabled: true,
				min: 0,
				max: 0,
				value: 0,
				step: 1
			});
			$("#current_date").html('----------');
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

    function load_next_sublayer() {
    	if ((current_sublayer + 1) >= animals_sublayers.length) {
    		load_sublayer(0);
    	} else {
    		load_sublayer(current_sublayer + 1);
    	}
    }
    
    function load_sublayer(i) {
    	if (current_sublayer != null) {
    		map.removeLayer(animals_sublayers[current_sublayer]);
    	}
    	current_sublayer = i;
    	map.addLayer(animals_sublayers[i]);
    	$("#slider" ).slider({ value: i });
    	$("#current_date" ).html(animals_features[i].properties.date);
    }

    function format_date(date) {
    	month = (date.getMonth() + 1).toString();
    	day = date.getDate().toString();
    	hours = date.getHours().toString();
    	minutes = date.getMinutes().toString();
    	seconds = date.getSeconds().toString();
    	return date.getFullYear().toString() + (month.length < 2 ? '0' + month : month) + (day.length < 2 ? '0' + day : day) + (hours.length < 2 ? '0' + hours : hours) +
    	(minutes.length < 2 ? '0' + minutes : minutes) + (seconds.length < 2 ? '0' + seconds : seconds);
    }

    function load_animals(start, end) {
        url = contextVariables.animals_json_url + '?';
        if (start != null) {
        	url += 'start=' + format_date(start) + '&'
        }
        if (end != null) {
        	url += 'end=' + format_date(end) + '&'
        }

    	animals_layer = new L.GeoJSON.AJAX(url,{
            pointToLayer: function (feature, latlng) {
                return new L.CircleMarker(latlng, getStyleForDevice(feature));
            },
            middleware: function(data) {
            	if (current_sublayer != null) {
            		map.removeLayer(animals_sublayers[current_sublayer]);
            		current_sublayer = null;
            	}
    			clearInterval(timer);
            	animals_sublayers = [];
            	animals_features = [];
            	return data;
            },
            onEachFeature: function (feature, layer) {
            	animals_sublayers.push(layer);
            	animals_features.push(feature);
                layer.bindPopup(feature.properties.popup);
            }
        });

    	animals_layer.on('data:loaded', function(e) {
    		stop_spinner();
            init_slider();
        	if (animals_sublayers.length > 0) {
        		load_sublayer(0);
        	} else {
        		$('#no-positions-modal').modal();
        	}
        });
    }

    function toggle_custom_time(active) {
    	if (active) {
			$("#date_selectors .active").removeClass('active');
			$("#update_time_custom").removeClass('inactive');
			$("#update_time_custom").addClass('active');
    	} else {
			$("#update_time_custom").removeClass('active');
			$("#update_time_custom").addClass('inactive');
    	}
    }
    
    function load_today_animals() {
		start_spinner($("#update_time_today")[0]);
		toggle_custom_time(false);
		today = new Date();
		today.setHours(0);
		today.setMinutes(0);
		today.setSeconds(0);
		load_animals(new Date(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate(), today.getUTCHours(), today.getUTCMinutes(), today.getUTCSeconds()),
				new Date(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()+1, today.getUTCHours(), today.getUTCMinutes(), today.getUTCSeconds()));
    }

    function start_spinner(component) {
    	stop_spinner();
		ladda = Ladda.create(component);
	 	ladda.start();
    }

    function stop_spinner() {
    	if (ladda != null) {
    		ladda.stop();
    		ladda = null;
    	}
    }

    NS.init = function(){
    	$("#slider").slider({disabled: true});
        $( ".datepicker" ).datepicker( $.datepicker.regional[ "es" ] );
        $("#pause").prop('disabled', true);
		$("#update_time_today").click(function(){
			load_today_animals();
		});
		$("#update_time_yesterday").click(function(){
			start_spinner(this);
			toggle_custom_time(false);
			today = new Date();
			today.setHours(0);
			today.setMinutes(0);
			today.setSeconds(0);
			load_animals(new Date(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()-1, today.getUTCHours(), today.getUTCMinutes(), today.getUTCSeconds()),
					new Date(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate(), today.getUTCHours(), today.getUTCMinutes(), today.getUTCSeconds()));
		});
		$("#update_time_last_week").click(function(){
			start_spinner(this);
			toggle_custom_time(false);
			today = new Date();
			today.setHours(0);
			today.setMinutes(0);
			today.setSeconds(0);
			load_animals(new Date(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()-6, today.getUTCHours(), today.getUTCMinutes(), today.getUTCSeconds()),
					new Date(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()+1, today.getUTCHours(), today.getUTCMinutes(), today.getUTCSeconds()));
		});
		$("#update_time_custom_confirm").click(function(){
			start_spinner(this);
			toggle_custom_time(true);
			start = $('#startdate').datepicker('getDate');
			if (start != null) {
				start = new Date(start.getUTCFullYear(), start.getUTCMonth(), start.getUTCDate(),  start.getUTCHours(), start.getUTCMinutes(), start.getUTCSeconds());
			}
			end = $('#enddate').datepicker('getDate');
			if (end != null) {
				end = new Date(end.getUTCFullYear(), end.getUTCMonth(), end.getUTCDate()+1,  end.getUTCHours(), end.getUTCMinutes(), end.getUTCSeconds());
			}
			load_animals(start, end);
		});
    	map = L.map('map_history', {zoomControl: false});
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
        load_today_animals();

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
