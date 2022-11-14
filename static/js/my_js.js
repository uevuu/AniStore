function checkValReg() {
    let forms = document.querySelectorAll('.needs-validation-reg')
    let password = document.getElementById("passwordInput")
    let confirmPassword = document.getElementById("confirmPasswordInput")
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault()
                    event.stopPropagation()
                }
                if (confirmPassword.value !== password.value) {
                    swal({
                        title: "Error",
                        text: "Password don't match",
                        icon: "warning",
                        buttons: {
                            cancel: 'Ok'
                        },
                    })
                    event.preventDefault()
                    event.stopPropagation()
                }
                form.classList.add('was-validated')
            }, false)
        })
}

function checkValLog() {
    let forms = document.querySelectorAll('.needs-validation-log')
    let password = document.getElementById("passwordLogInput")
    let isGoodPassword = /(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}/g
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault()
                    event.stopPropagation()
                } else if (!isGoodPassword.test(password.value)) {
                    swal({
                        title: "Password",
                        text: "contains at least one number" + "\r\n" +
                            "contains at least one special character" + "\r\n" +
                            "contains at least one Latin letter in lowercase" + "\r\n" +
                            "contains at least one Latin letter in uppercase" + "\r\n" +
                            "consists of at least 6 characters",
                        icon: "warning",
                        buttons: {
                            cancel: 'Ok'
                        },
                    })
                    event.preventDefault()
                    event.stopPropagation()
                }
                form.classList.add('was-validated')
            }, false)
        })
}


function checkValProfileEdit() {
    let forms = document.querySelectorAll('.needs-validation-log')
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault()
                    event.stopPropagation()
                }
                form.classList.add('was-validated')
            }, false)
        })
}