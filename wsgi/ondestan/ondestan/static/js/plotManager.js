var ladda;
var plots;
var nominatimResults;
var nominatimItems = [];
var nominatimBaseUrl = "http://nominatim.openstreetmap.org/search?format=json&limit=5";
if (window.contextVariables.admin_mail != "") {
	nominatimBaseUrl += "&email=" + window.contextVariables.admin_mail;
}

function centerOnNominatimResult(i) {
	$('#plot_locator_modal').modal('hide');
	centerMapOnPosition(nominatimResults[i].lat, nominatimResults[i].lon);
}

function displayNominatimResults() {
	nominatimItems = [];
	content = "";
	for (i = 0, len = nominatimResults.length; i < len; i++) {
		if (!(nominatimResults[i].display_name in nominatimItems)) {
			content += '<a href="#" class="list-group-item" onclick="centerOnNominatimResult(' + i + ')">' + nominatimResults[i].display_name + '</a>';
			nominatimItems[nominatimResults[i].display_name] = true;
		}
	}
	$('#plot_locator_place_results_list').html(content);
}

function startSpinner(component) {
	stopSpinner();
	ladda = Ladda.create(component);
 	ladda.start();
}

function stopSpinner() {
	if (ladda != null) {
		ladda.stop();
		ladda = null;
	}
}

function validatePlotData() {
	if (( $('#plot_owner').val() != '' || !$('#plot_owner').is(":visible") ) && $('#plot_name').val() != '') {
		$('#accept_btn').prop('disabled', false);
	} else {
		$('#accept_btn').prop('disabled', true);
	}
}
validatePlotData();

function addToList(feature){
    var plot = feature.properties;
    var zoomString = '<span class="glyphicon glyphicon-search"></span> ';
    if (plot.centroid){
        var lng = plot.centroid.coordinates[0];
        var lat = plot.centroid.coordinates[1];
        zoomString = '<a href="#" onclick="zoom('+lng+','+lat+')"><span class="glyphicon glyphicon-screenshot" disabled></span>  </a>';
    }
    var name = plot.name || plot.id;
    var toggleClass = 'toggle_' + plot.id;
    return '<li class="list-group-item">' +
    	'<form role="form" class="form-inline" action="' + contextVariables.update_plot_name_url + '" method="post">' +
        '<input type="hidden" id="id" name="id" style="display: none;" value="' + plot.id + '"/>' +
        zoomString +
        '<input class="form-control '+toggleClass+'" type="text" id="name" style="display: none;" name="name" value="' + (plot.name || '') + '" />' +
        '<label data-toggle="tooltip" data-placement="top" title="' + contextVariables.edit_name_tooltip + '" class="'+toggleClass+'" ondblclick="$(\'.'+toggleClass+'\').toggle(0)">' + name + '</label>'+
        (contextVariables.is_admin ? ('<span class="plot_owner">' + plot.owner + '</span>') : '') +
        '</form>' +
        '</li>';
}

function request_plots_layer() {
    plots_list_content = '';
	var plots = new L.FeatureGroup();
	plots_layer = new L.GeoJSON.AJAX(contextVariables.plots_json_url,{
//		    style: function (feature) {
//		        return {clickable: false};
//		    },
        middleware: function(data) {
            for (i = 0, len = data.length; i < len; i++) {
            	plots_list_content += addToList(data[i]);
            }
            return data;
        },
        onEachFeature: function (feature, layer) {
        	if (feature.properties.popup != null && feature.properties.popup != '') {
        		layer.bindPopup(feature.properties.popup);
        	}
        	plots.addLayer(layer);
        }
    });

	plots_layer.on('data:loaded', function(e) {
		if (plots_list_content != '') {
			$('#no_plots_message').hide();
			$('#plots_list_content').html(plots_list_content);
			$( "[data-toggle='tooltip']" ).tooltip({delay: {show: 750, hide: 0}});
		} else {
			$('#plots_list_content').html('');
			$('#no_plots_message').show();
		}
	});

	return plots;
}

function load_data() {
	plots = request_plots_layer();
	map.addLayer(plots);
}

function additionalControls() {
	controls = []
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
	    },
	    position: 'topleft'
	};

	controls.push(new L.Control.Draw(drawOptions));

	map.on('draw:created', function (e) {
		var layer = e.layer, url = window.contextVariables.create_plot_url + "?";
		for (i in layer._latlngs) {
			url += 'x' + i + '=' + layer._latlngs[i].lng + '&y' + i + '=' + layer._latlngs[i].lat + '&'
		}
		var url = url.substring(0, url.length - 1);
		$('#accept_btn').off();
		$('#accept_btn').click(function() {
			$('#plot_modal').modal('hide');
			url += '&name=' + $('#plot_name').val();
			url += '&userid=' + $('#plot_owner').val();
			$.ajax({url: url,success:function(result){
				if (result.success) {
					layer.feature = result.feature;
	                layer.bindPopup(result.feature.properties.popup);
	    			plots.addLayer(layer);
					request_plots_layer();
				}
			}});
		});
		$('#plot_modal').modal();
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
					request_plots_layer();
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
					request_plots_layer();
				}
			}});
		}
	});
	return controls
}

$('#plot_owner').change(validatePlotData);
$('#plot_name').keyup(validatePlotData);

$('#plot_locator_btn').click(function() {
	$('#plot_locator_options').show();
	$('.plot_locator_option').hide();
	$('#plot_locator_accept_btn').prop('disabled', true);
	$('#plot_locator_modal').modal();
});
$('#plot_locator_option_current_position').click(function() {
	getLocation();
	$('#plot_locator_modal').modal('hide');
});
$('#location').bind("enterKey",function(e){
	$('#plot_locator_accept_btn').click();
});
$('#location').keyup(function(e){
    if(e.keyCode == 13)
    {
        $(this).trigger("enterKey");
    }
});
$('#plot_locator_option_place_name').click(function() {
	$('#plot_locator_options').hide();
	$('#plot_locator_place').show();
	$('#plot_locator_accept_btn').off();
	$('#plot_locator_accept_btn').prop('disabled', false);
	$('#plot_locator_accept_btn').click(function() {
		startSpinner(this);
		$.getJSON( nominatimBaseUrl + '&q=' + $('#location').val(), function( data ) {
			stopSpinner();
			nominatimResults = data;
			displayNominatimResults();
			$('#plot_locator_place').hide();
			$('#plot_locator_place_results').show();
			$('#plot_locator_accept_btn').prop('disabled', true);
		});
	});
	$('#plot_locator_modal').modal();
});
