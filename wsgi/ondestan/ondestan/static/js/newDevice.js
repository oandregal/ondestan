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
			return false;
		},
		rules : {
			imei : "required"
		}
	});
});
