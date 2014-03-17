function checkFields() {
	login = document.getElementById('login').value;
	name = document.getElementById('name').value;
	email = document.getElementById('email').value;
	pass1 = document.getElementById('password1').value;
	pass2 = document.getElementById('password2').value;
	document.getElementById('submit').disabled = ((pass1 != pass2) || (pass1 == '') || (login == '') || (name == '') || (email == ''));
	if (pass1 != '') {
	if (pass1.length < 6) {
		document.getElementById('passtooshort').style.display="";
		document.getElementById('passdistinct').style.display="none";
	} else {
		document.getElementById('passtooshort').style.display="none";
	if ((pass2 != '') && (pass1 != pass2)) {
		document.getElementById('passdistinct').style.display="";
	} else {
		document.getElementById('passdistinct').style.display="none";
	}
	}
	}
}