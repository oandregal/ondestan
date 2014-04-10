if (contextVariables.orders_popover_content != '') {
    $('#new_devices').popover({
        html: true,
        placement: 'bottom',
        trigger: 'hover',
        content: '<ul class="list-unstyled">' + contextVariables.orders_popover_content + '</ul>',
    });
}
