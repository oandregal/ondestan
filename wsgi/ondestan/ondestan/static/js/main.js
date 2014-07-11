$(function(){
	$(".dropdown-toggle").dropdown();
	if (contextVariables.orders_popover_content != '') {
	    $('#new_devices').popover({
	        html: true,
	        placement: 'left',
	        trigger: 'hover',
	        content: '<ul class="list-unstyled">' + contextVariables.orders_popover_content + '</ul>',
	    });
	}
});
