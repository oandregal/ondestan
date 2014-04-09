if (contextVariables.orders_popover_content != '') {
	$('#new_devices').popover({
	    html: true,
	    placement: 'bottom',
	    trigger: 'hover',
	    content: '<ul class="list-unstyled">' + contextVariables.orders_popover_content + '</ul>',
	});
}

$( function() {
	var map = L.map('map').setView([42.25, -7.54], 13);
	var active_devices = [];
	var active_devices_popover_content = '';
	var inactive_devices = [];
	var inactive_devices_popover_content = '';
	var low_battery_devices = [];
	var low_battery_devices_popover_content = '';

	function load_animals() {
		layer = new L.GeoJSON.AJAX(contextVariables.animals_json_url,{
			pointToLayer: function (feature, latlng) {
				var color = "green";
				var weight = 0;
	            if (feature.properties.battery < 20.0) {
	            	color = "red";
	            	if (feature.properties.active) {
		            	low_battery_devices.push(feature);
						if ((feature.properties.name != null) && (feature.properties.name != '')) {
							name = feature.properties.name;
						} else {
							name = feature.properties.id;
						}
						low_battery_devices_popover_content += '<li>' + name + ' (' + feature.properties.battery + '%)</li>';
	            	}
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
            middleware: function(data) {
            	for (i = 0, len = data.length; i < len; i++) {
    				if (data[i].properties.active) {
    					active_devices.push(data[i]);
    					if ((data[i].properties.name != null) && (data[i].properties.name != '')) {
    						name = data[i].properties.name;
    					} else {
    						name = data[i].properties.id;
    					}
    					if ((data[i].properties.battery != null) && (data[i].properties.battery != '')) {
    						battery = data[i].properties.battery + '%';
    					} else {
    						battery = '---';
    					}
    					url = contextVariables.deactivate_device_url.replace('__device_id__', data[i].properties.id);
    					active_devices_popover_content += '<li><img data-toggle="tooltip" data-placement="left" title="' + contextVariables.edit_image_tooltip + '" class="left" src="' + contextVariables.edit_image_url + '" onclick="$(\'#active_name_' + data[i].properties.id + '\').toggle(0);$(\'#active_form_' + data[i].properties.id + '\').toggle(0);"/>' + 
    					'<div class="left" id="active_name_' + data[i].properties.id + '">' + name + ' (' + battery + ')</div>' + 
    					'<form role="form" id="active_form_' + data[i].properties.id + '" class="form-inline left" action="' + contextVariables.update_animal_name_url + '" method="post" style="display: none;"><input type="hidden" id="id" name="id" value="' + data[i].properties.id + '"/>' + 
    					'<input class="form-control" type="text" id="name" name="name" value="' + data[i].properties.name + '" />' + '</form>' + 
    					'<a href="' + url + '" type="button" class="btn btn-default btn-xs right">' + contextVariables.deactivate_device_msg + '</a></li>';
    				} else {
    					inactive_devices.push(data[i]);
    					if ((data[i].properties.name != null) && (data[i].properties.name != '')) {
    						name = data[i].properties.name;
    					} else {
    						name = data[i].properties.id;
    					}
    					url = contextVariables.activate_device_url.replace('__device_id__', data[i].properties.id);
    					inactive_devices_popover_content += '<li><img data-toggle="tooltip" data-placement="left" title="' + contextVariables.edit_image_tooltip + '" class="left" src="' + contextVariables.edit_image_url + '" onclick="$(\'#inactive_name_' + data[i].properties.id + '\').toggle(0);$(\'#inactive_form_' + data[i].properties.id + '\').toggle(0);"/>' + 
    					'<div class="left" id="inactive_name_' + data[i].properties.id + '">' + name + '</div>' + 
    					'<form role="form" id="inactive_form_' + data[i].properties.id + '" class="form-inline left" action="' + contextVariables.update_animal_name_url + '" method="post" style="display: none;"><input type="hidden" id="id" name="id" value="' + data[i].properties.id + '"/>' + 
    					'<input class="form-control" type="text" id="name" name="name" value="' + data[i].properties.name + '" />' + '</form>' + 
    					'<a href="' + url + '" type="button" class="btn btn-default btn-xs right">' + contextVariables.activate_device_msg + '</a></li>';
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
				    content: '<ul id="active_devices_popover_content" class="list-unstyled">' + active_devices_popover_content + '</ul>',
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

	new L.GeoJSON.AJAX(contextVariables.plots_json_url,{
        onEachFeature: function (feature, layer) {
            layer.bindPopup(feature.properties.popup);
        },
        middleware:function(data){
            load_animals();
            return data;
        }
	}).addTo(map);

    L.tileLayer('http://a.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	    maxZoom: 18,
	    attribution: '<a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
    }).addTo(map);

});
