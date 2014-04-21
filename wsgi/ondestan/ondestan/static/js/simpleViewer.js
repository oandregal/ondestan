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
            noData: '--- ',
        },
        color: {
            high:     "green",
            middle:   "yellow",
            low:      "red",
            inactive: "grey",
        },
        opacity:{
            active: 1,
            inactive: 0.3,
        }
    };

    function getStyleForDevice(feature){
        var device = feature.properties;
        var optionsDefault = {
            stroke: false,
            radius: 8,
            fillColor: batteryStandards.color.high,
            fillOpacity: batteryStandards.opacity.active
        };
        var opt = optionsDefault;

        if(!device.active){
            opt.fillColor = batteryStandards.color.inactive;
            opt.fillOpacity = batteryStandards.opacity.inactive;
        } else if (device.battery < batteryStandards.level.low) {
            opt.fillColor = batteryStandards.color.low;
        } else if (device.battery < batteryStandards.level.middle) {
            opt.fillColor = batteryStandards.color.middle;
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
            ' <a href="' + url + '" type="button" class="pull-right btn btn-default btn-xs '+toggleClass+'">' + activation + '</a> ' +
            zoomString +
            '<span class="'+toggleClass+'" ondblclick="$(\'.'+toggleClass+'\').toggle(0)">' + name + '</span>'+
            '<span class="badge '+toggleClass+'">' + battery + '%</span>' +
            '<form role="form" class="form-inline '+toggleClass+'" action="' + contextVariables.update_animal_name_url + '" method="post" style="display: none;">' +
            '<input type="hidden" id="id" name="id" value="' + device.id + '"/>' +
            '<input class="form-control" type="text" id="name" name="name" value="' + name + '" />' +
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
        map = L.map('map').setView([42.25, -7.54], 13);

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
    };

    // Init on document ready
    $(function(){
        NS.init();
    });

})(window.OE = window.OE || {});
