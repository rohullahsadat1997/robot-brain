document.addEventListener("DOMContentLoaded", () => {

    const loginForm = document.getElementById("loginForm");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const loginButton = document.getElementById("loginButton");
    const errorBox = document.getElementById("errorBox");
    const togglePassword = document.getElementById("togglePassword");


    /* =========================
       Safety Check
    ========================= */

    if (
        !loginForm ||
        !emailInput ||
        !passwordInput ||
        !loginButton
    ) {
        console.error(
            "Login form elements were not found."
        );

        return;
    }


    /* =========================
       Password Visibility
    ========================= */

    if (togglePassword) {

        togglePassword.addEventListener(
            "click",
            () => {

                const isPassword =
                    passwordInput.type === "password";

                passwordInput.type =
                    isPassword
                        ? "text"
                        : "password";

                togglePassword.textContent =
                    isPassword
                        ? "◉"
                        : "◌";

                togglePassword.setAttribute(
                    "aria-label",
                    isPassword
                        ? "Hide password"
                        : "Show password"
                );
            }
        );
    }


    /* =========================
       Error Handling
    ========================= */

    function showError(message) {

        if (!errorBox) {
            return;
        }

        errorBox.textContent =
            message || "Something went wrong.";

        errorBox.style.display = "block";
    }


    function hideError() {

        if (!errorBox) {
            return;
        }

        errorBox.textContent = "";

        errorBox.style.display = "none";
    }


    /* =========================
       Loading State
    ========================= */

    function setLoading(isLoading) {

        loginButton.disabled =
            isLoading;

        if (isLoading) {

            loginButton.classList.add(
                "loading"
            );

            loginButton.textContent =
                "Signing in...";

        } else {

            loginButton.classList.remove(
                "loading"
            );

            loginButton.textContent =
                "Sign in to Brain";
        }
    }


    /* =========================
       Login Request
    ========================= */

    loginForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();

            hideError();


            const email =
                emailInput.value.trim();

            const password =
                passwordInput.value;


            /* =========================
               Basic Validation
            ========================= */

            if (!email || !password) {

                showError(
                    "Please enter your email and password."
                );

                return;
            }


            setLoading(true);


            try {

                const response =
                    await fetch(
                        "/api/auth/login/",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            credentials:
                                "same-origin",

                            body:
                                JSON.stringify({
                                    email: email,
                                    password: password
                                })
                        }
                    );


                let data = {};

                try {

                    data =
                        await response.json();

                } catch {

                    data = {};
                }


                /* =========================
                   API Error
                ========================= */

                if (!response.ok) {

                    throw new Error(
                        data.error ||
                        data.detail ||
                        "Email or password is incorrect."
                    );
                }


                /* =========================
                   Successful Login
                ========================= */

                loginButton.classList.remove(
                    "loading"
                );

                loginButton.textContent =
                    "Welcome back ✓";


                setTimeout(() => {

                    window.location.href = "/";

                }, 500);


            } catch (error) {

                console.error(
                    "Login error:",
                    error
                );


                showError(
                    error.message ||
                    "Unable to sign in. Please try again."
                );


                setLoading(false);
            }
        }
    );


    /* =========================
       Clear Error While Typing
    ========================= */

    emailInput.addEventListener(
        "input",
        hideError
    );

    passwordInput.addEventListener(
        "input",
        hideError
    );


    /* =========================
       Desktop Focus
    ========================= */

    if (window.innerWidth > 600) {

        emailInput.focus();
    }

});