$.validator.addMethod("mobile", function(phone_number, element) {
	phone_number = phone_number.replace(/\s+/g, "");
	return this.optional(element) || /^(\+[0-9]{1,4})?[6|7][0-9]{8}$/.test(phone_number);
}, "Please specify a valid mobile phone number.");