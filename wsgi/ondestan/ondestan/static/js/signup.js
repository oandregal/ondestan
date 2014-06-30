$.extend($.validator.messages, {
	required : window.contextVariables.required_field_msg,
	minlength : jQuery.validator
			.format(window.contextVariables.minlength_field_msg),
	email : window.contextVariables.email_field_msg,
	mobile : window.contextVariables.mobile_field_msg
});
$(function() {
	$('#form').validate({
		rules : {
			name : "required",
			phone : "mobile",
			email : {
				email : true,
				required : true,
				remote : {
					url : window.contextVariables.check_email_url,
					type : 'post',
					data : {
						email : function() {
							return $('#form :input[name="email"]').val();
						}
					}
				}
			},
			password : {
				required : true,
				minlength : 6
			},
			password2 : {
				equalTo : "#password"
			}
		},
		messages : {
			password2 : {
				equalTo : window.contextVariables.passwords_dont_match_msg
			}
		}
	});
});