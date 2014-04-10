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
    var batteryStandards = {
        level: {
            low: 20.0,
            middle: 50.0,
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

    function addToPopover(device){
        var name = device.name || device.imei;
        var battery = device.battery || '---';
        var url = contextVariables.deactivate_device_url.replace('__device_id__', device.id);
        var elID = 'name_' + device.id;
        var formID = 'form_' + device.id;
        var msg = contextVariables.deactivate_device_msg;
        if(!device.active){
            url = contextVariables.activate_device_url.replace('__device_id__', device.id);
            msg = contextVariables.activate_device_msg;
        }
        return '<li>' +
            '<img data-toggle="tooltip" data-placement="left" title="' + contextVariables.edit_image_tooltip + '" class="left" src="' + contextVariables.edit_image_url + '" onclick="$(\'#'+elID+'\').toggle(0);$(\'#'+formID+'\').toggle(0);"/>' +
            '<div class="left" id="'+elID+'">' + name + ' (' + battery + ' %)</div>' +
            '<form role="form" id="'+formID+'" class="form-inline left" action="' + contextVariables.update_animal_name_url + '" method="post" style="display: none;">' +
            '<input type="hidden" id="id" name="id" value="' + device.id + '"/>' +
            '<input class="form-control" type="text" id="name" name="name" value="' + name + '" />' +
            '</form>' +
            '<a href="' + url + '" type="button" class="btn btn-default btn-xs right">' + msg + '</a>';
            '</li>';
    }

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
                            low_battery_devices_popover_content += addToPopover(device);
                        }
                        active_devices.push(data[i]);
                        active_devices_popover_content += addToPopover(device);
                    } else {
                        inactive_devices.push(data[i]);
                        inactive_devices_popover_content += addToPopover(device);
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
