window.onload = function() {
    var recaptcha = document.forms["form-login"]["g-recaptcha-response"];
    recaptcha.required = true;
    recaptcha.oninvalid = function(e) {alert("Por favor complete o reCAPTCHA.");}
}