document.addEventListener("DOMContentLoaded", () => {

    const registerForm =
        document.getElementById("registerForm");

    const registerButton =
        document.getElementById("registerButton");

    const message =
        document.getElementById("message");

    const usernameInput =
        document.getElementById("username");

    const emailInput =
        document.getElementById("email");

    const passwordInput =
        document.getElementById("password");

    const confirmPasswordInput =
        document.getElementById("confirmPassword");


    /* ========================================
       SAFETY CHECK
    ======================================== */

    if (
        !registerForm ||
        !registerButton ||
        !message ||
        !usernameInput ||
        !emailInput ||
        !passwordInput ||
        !confirmPasswordInput
    ) {
        console.error(
            "Register form elements not found."
        );

        return;
    }


    /* ========================================
       MESSAGE
    ======================================== */

    function showMessage(
        text,
        type = "error"
    ) {

        message.textContent =
            text || "";

        if (type === "success") {

            message.style.color =
                "#047857";

        } else {

            message.style.color =
                "#dc2626";
        }
    }


    function clearMessage() {

        message.textContent = "";

        message.style.color =
            "";
    }


    /* ========================================
       FORM SUBMIT
    ======================================== */

    registerForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();


            const username =
                usernameInput.value.trim();

            const email =
                emailInput.value.trim();

            const password =
                passwordInput.value;

            const confirmPassword =
                confirmPasswordInput.value;


            clearMessage();


            /* ========================================
               CLIENT VALIDATION
            ======================================== */

            if (!username) {

                showMessage(
                    "Please enter a username."
                );

                usernameInput.focus();

                return;
            }


            if (!email) {

                showMessage(
                    "Please enter your email."
                );

                emailInput.focus();

                return;
            }


            if (!password) {

                showMessage(
                    "Please enter a password."
                );

                passwordInput.focus();

                return;
            }


            if (password !== confirmPassword) {

                showMessage(
                    "Passwords do not match."
                );

                confirmPasswordInput.focus();

                return;
            }


            /* ========================================
               LOADING
            ======================================== */

            registerButton.disabled =
                true;

            registerButton.textContent =
                "Creating account...";


            try {

                const response =
                    await fetch(
                        "/api/auth/register/",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Accept":
                                    "application/json"
                            },

                            credentials:
                                "same-origin",

                            body:
                                JSON.stringify({
                                    username:
                                        username,

                                    email:
                                        email,

                                    password:
                                        password
                                })
                        }
                    );


                let data = {};

                try {

                    data =
                        await response.json();

                } catch (jsonError) {

                    data = {};
                }


                /* ========================================
                   ERROR
                ======================================== */

                if (!response.ok) {

                    showMessage(
                        data.error ||
                        "Registration failed."
                    );

                    return;
                }


                /* ========================================
                   SUCCESS
                ======================================== */

                showMessage(
                    "Account created successfully!",
                    "success"
                );


                registerButton.textContent =
                    "Account Created ✓";


                setTimeout(
                    () => {

                        window.location.href =
                            "/";

                    },
                    800
                );

            } catch (error) {

                console.error(
                    "Registration error:",
                    error
                );


                showMessage(
                    "Something went wrong. Please try again."
                );

            } finally {

                /*
                 * If registration succeeded,
                 * the button stays in success state
                 * until redirect.
                 */

                if (
                    registerButton.textContent !==
                    "Account Created ✓"
                ) {

                    registerButton.disabled =
                        false;

                    registerButton.textContent =
                        "Create Account";
                }
            }

        }
    );


    /* ========================================
       CLEAR ERROR WHILE TYPING
    ======================================== */

    [
        usernameInput,
        emailInput,
        passwordInput,
        confirmPasswordInput
    ].forEach((input) => {

        input.addEventListener(
            "input",
            () => {

                if (message.textContent) {

                    clearMessage();
                }

            }
        );

    });


    /* ========================================
       PASSWORD MATCH INDICATOR
    ======================================== */

    confirmPasswordInput.addEventListener(
        "input",
        () => {

            if (
                confirmPasswordInput.value &&
                passwordInput.value !==
                confirmPasswordInput.value
            ) {

                confirmPasswordInput.style.borderColor =
                    "#dc2626";

            } else {

                confirmPasswordInput.style.borderColor =
                    "";
            }

        }
    );


    /* ========================================
       INITIAL FOCUS
    ======================================== */

    if (
        window.innerWidth > 600
    ) {

        usernameInput.focus();
    }

});