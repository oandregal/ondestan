$.extend($.validator.messages, {
	required : window.contextVariables.required_field_msg
});
$( "div[data-toggle='tooltip']" ).attr('title', function(index, atr) {
	return $(this).attr('tooltip-msg');
});
$( "div[data-toggle='tooltip']" ).tooltip();
$(function() {
	$('#form').validate({
		errorPlacement : function(error, element) {
			if (error[0].childNodes.length > 0 && 'data' in error[0].childNodes[0]) {
				$(element).attr('title', error[0].childNodes[0].data);
				$(element).tooltip('destroy');
				$(element).tooltip({
					placement: 'bottom'
				});
			}
			return false;
		},
		success : function(label, element) {
			$(element).removeAttr('title');
			$(element).tooltip('destroy');
		},
		rules : {
			imei : {
				required: true,
				"remote" : {
					url : window.contextVariables.check_imei_url,
					type : 'post',
					data : {
						imei : function() {
							return $('#form :input[name="imei"]').val();
						}
					}
				}
			}
		}
	});
});
