(function(NS) {

    var map;
    var active_devices = [];
    var active_devices_popover_content = '';
    var inactive_devices = [];
    var inactive_devices_popover_content = '';
    var low_battery_devices = [];
    var low_battery_devices_popover_content = '';
    var batteryStandards = {
        level: {
            low: window.contextVariables.low_battery_barrier,
            middle: window.contextVariables.medium_battery_barrier,
            noData: '---',
        },
        color: {
            high:     "green",
            middle:   "yellow",
            low:      "red",
            inactive: "grey",
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

    function addToPopover(feature){
        var device = feature.properties;
        var zoomString = '<span class="glyphicon glyphicon-search"></span> ';
        if (feature.geometry){
            var lng = feature.geometry.coordinates[0];
            var lat = feature.geometry.coordinates[1];
            zoomString = '<a href="#" onclick="window.OE.zoom('+lng+','+lat+')"><span class="glyphicon glyphicon-search" disabled></span>  </a>';
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

    function load_animals() {

        layer = new L.GeoJSON.AJAX(contextVariables.animals_json_url,{
            pointToLayer: function (feature, latlng) {
                return new L.CircleMarker(latlng, getStyleForDevice(feature));
            },
            middleware: function(data) {
                for (i = 0, len = data.length; i < len; i++) {
                    var device = data[i].properties;
                    if (device.active) {
                        if (device.battery < batteryStandards.level.low) {
                            low_battery_devices.push(data[i]);
                            low_battery_devices_popover_content += addToPopover(data[i]);
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

        layer.on('data:loaded', function(e) {

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

            $('#low_battery_devices').text(low_battery_devices.length);
            if (low_battery_devices_popover_content != '') {
                $('#low_battery_devices').removeAttr('disabled');
                $('#low_battery_devices').popover({
                    html: true,
                    placement: 'bottom',
                    trigger: 'click',
                    content: '<ul class="list-unstyled">' + low_battery_devices_popover_content + '</ul>',
                });
            }

        });

        layer.addTo(map);
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

    	var plots = new L.FeatureGroup();
		new L.GeoJSON.AJAX(contextVariables.plots_json_url,{
//		    style: function (feature) {
//		        return {clickable: false};
//		    },
            onEachFeature: function (feature, layer) {
            	if (feature.properties.popup != null && feature.properties.popup != '') {
            		layer.bindPopup(feature.properties.popup);
            	}
            	plots.addLayer(layer);
            },
            middleware:function(data){
                load_animals();
                return data;
            }
        });

    	map.addLayer(plots);

    	var drawOptions = {
		    draw: {
		        polyline: false,
		        polygon: {
		        	showArea: true, // Show the area of the drawn polygon
		            allowIntersection: false, // Restricts shapes to simple polygons
		            drawError: {
		                color: '#FF0000' // Color the shape will turn when intersects
		            },
		            shapeOptions: {
		                color: '#0033ff'
		            }
		        },
		        circle: false, // Turns off this drawing tool
		        rectangle: false,
		        marker: false
		    },
		    edit: {
		    	featureGroup: plots
		    }
		};

		map.on('draw:created', function (e) {
			if (window.contextVariables.is_admin) {
				var layer = e.layer, url = window.contextVariables.create_plot_url + "?";
				for (i in layer._latlngs) {
					url += 'x' + i + '=' + layer._latlngs[i].lng + '&y' + i + '=' + layer._latlngs[i].lat + '&'
				}
				var url = url.substring(0, url.length - 1);
				$('#accept_btn').off();
				$('#accept_btn').click(function() {
					$('#my_modal').modal('hide');
					url += '&userid=' + $('#user_selector').val();
					$.ajax({url: url,success:function(result){
						if (result.success) {
							layer.feature = result.feature;
			                layer.bindPopup(result.feature.properties.popup);
			    			plots.addLayer(layer);
						}
					}});
				});
				$('#my_modal').modal();
			} else {
				var layer = e.layer, url = window.contextVariables.create_plot_url + "?";
				for (i in layer._latlngs) {
					url += 'x' + i + '=' + layer._latlngs[i].lng + '&y' + i + '=' + layer._latlngs[i].lat + '&'
				}
				url = url.substring(0, url.length - 1);
				$.ajax({url: url,success:function(result){
					if (result.success) {
						layer.feature = result.feature;
		                layer.bindPopup(result.feature.properties.popup);
		    			plots.addLayer(layer);
					}
				}});
			}
		});
		map.on('draw:edited', function (e) {
			var layers = e.layers._layers, url;
			for (j in layers) {
				url = window.contextVariables.update_plot_geom_url + "?"
				layer = layers[j];
				for (i in layer._latlngs) {
					url += 'x' + i + '=' + layer._latlngs[i].lng + '&y' + i + '=' + layer._latlngs[i].lat + '&'
				}
				url += 'id=' + layer.feature.properties.id;
				$.ajax({url: url,success:function(result){
					if (result.success) {
						layer.feature = result.feature;
					}
				}});
			}
		});
		map.on('draw:deleted', function (e) {
			var layers = e.layers._layers, url;
			for (j in layers) {
				url = window.contextVariables.delete_plot_url + "?"
				layer = layers[j];
				url += 'id=' + layer.feature.properties.id;
				$.ajax({url: url,success:function(result){
					if (result.success) {
					}
				}});
			}
		});

		$('#user_selector').change(function() {
			if ($(this).val() != '') {
				$('#accept_btn').prop('disabled', false);
			} else {
				$('#accept_btn').prop('disabled', true);
			}
		});

		var drawControl = new L.Control.Draw(drawOptions);
		map.addControl(drawControl);

        L.tileLayer('http://a.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: '<a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
        }).addTo(map);
    };

    // Init on document ready
    $(function(){
        NS.init();
    });

})(window.OE = window.OE || {});
