(function(NS) {

	var plots;
    var map;

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
            zoomString = '<a href="#" onclick="window.OE.zoom('+lng+','+lat+')"><span class="glyphicon glyphicon-screenshot" disabled></span>  </a>';
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

    NS.zoom = function(lng, lat){
        var offset = 0.002;
        var southWest = L.latLng(lat-offset, lng-offset),
        northEast = L.latLng(lat+offset, lng+offset),
        bounds = L.latLngBounds(southWest, northEast);
        map.fitBounds(bounds);
    };
    
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

    function load_plots() {
    	plots = request_plots_layer();
    	map.addLayer(plots);
    }

    NS.init = function(){
    	map = L.map('map_plots', {zoomControl: false});
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

		$('#plot_owner').change(validatePlotData);
		$('#plot_name').keyup(validatePlotData);

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

		var drawControl = new L.Control.Draw(drawOptions);
		map.addControl(drawControl);

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
