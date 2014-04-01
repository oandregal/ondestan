$.extend($.validator.messages, {
	required : window.contextVariables.required_field_msg,
	digits : window.contextVariables.digits_field_msg
});
$(function() {
	$('#form').validate({
		errorPlacement : function(error, element) {
			return false;
		},
		rules : {
			units : {
				required : true,
				digits : true,
			},
			address : "required"
		}
	});
});