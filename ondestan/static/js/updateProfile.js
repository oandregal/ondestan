$.extend($.validator.messages, {
	required : window.contextVariables.required_field_msg,
	minlength : jQuery.validator
			.format(window.contextVariables.minlength_field_msg),
	email : window.contextVariables.email_field_msg
});
$(function() {
	$('#form').validate({
		rules : {
			login : {
				required : true,
				"remote" : {
					url : 'check_login',
					type : 'post',
					data : {
						login : function() {
							return $('#form :input[name="login"]').val();
						},
						id : function() {
							return $('#form :input[name="id"]').val();
						},
					}
				}
			},
			name : "required",
			email : {
				email : true,
				required : true,
				"remote" : {
					url : 'check_email',
					type : 'post',
					data : {
						email : function() {
							return $('#form :input[name="email"]').val();
						},
						id : function() {
							return $('#form :input[name="id"]').val();
						},
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