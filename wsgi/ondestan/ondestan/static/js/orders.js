(function(NS){

    function row(data){
        return '<tr id="order_'+data.id+'">'+
            '<td><a href="#">'+data.id+'</a></td>'+
            '<td>'+data.username+'</td>'+
            '<td>'+data.state+'</td>'+
            '<td>'+data.units+'</td>'+
            '<td>'+data.address+'</td>'+
            '</tr>';
    };

    function popoverContent(data){
        var list = '';
        $.each(data.states, function(k, v){
           list += '<li class="list-group-item">'+v.state+' el '+v.date+' </li>'
        });
        return list;
    };

    NS.init = function(){
        $.getJSON('orders.json', function(data){
            $.each(data['pending'], function(k, v){
                $('#pending_orders tbody').append(row(v));
                $('#order_'+v.id+' > td :first-child').popover({
                    html: true,
                    placement: 'right',
                    trigger: 'hover',
                    content: '<ul class="list-group">'+popoverContent(v)+'</ul>'
                });

            });
            $.each(data['processed'], function(k, v){
                $('#processed_orders tbody').append(row(v));
                $('#order_'+v.id+' > td :first-child').popover({
                    html: true,
                    placement: 'right',
                    trigger: 'hover',
                    content: '<ul class="list-group">'+popoverContent(v)+'</ul>'
                });
            });
        });
    };

    // Init on document ready
    $(function(){
        NS.init();
    });

})(window.OE = window.OE || {});
