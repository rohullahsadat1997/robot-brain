document.addEventListener("DOMContentLoaded", () => {

    const usernameElement =
        document.getElementById("username");

    const emailElement =
        document.getElementById("email");

    const avatarElement =
        document.getElementById("avatar");

    const accountStatusElement =
        document.getElementById("accountStatus");

    const accountContentElement =
        document.getElementById("accountContent");

    const profileUsernameElement =
        document.getElementById("profileUsername");

    const profileEmailElement =
        document.getElementById("profileEmail");

    const profileIdElement =
        document.getElementById("profileId");

    const usageNumberElement =
        document.getElementById("usageNumber");

    const usageUsedElement =
        document.getElementById("usageUsed");

    const usageLimitElement =
        document.getElementById("usageLimit");

    const usageProgressElement =
        document.getElementById("usageProgress");

    const subscriptionPlanElement =
        document.getElementById("subscriptionPlan");

    const logoutButton =
        document.getElementById("logoutButton");


    /* ========================================
       HELPERS
    ======================================== */

    function setText(element, value) {

        if (!element) {
            return;
        }

        element.textContent =
            value ?? "";
    }


    function setStatus(text, background, color) {

        if (!accountStatusElement) {
            return;
        }

        accountStatusElement.textContent =
            text;

        if (background) {
            accountStatusElement.style.background =
                background;
        }

        if (color) {
            accountStatusElement.style.color =
                color;
        }
    }


    function getInitial(username) {

        if (!username) {
            return "👤";
        }

        return username
            .charAt(0)
            .toUpperCase();
    }


    /* ========================================
       LOAD ACCOUNT
    ======================================== */

    async function loadAccount() {

        try {

            const response = await fetch(
                "/api/auth/account/",
                {
                    method: "GET",
                    credentials: "same-origin",
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );


            let data = {};

            try {

                data = await response.json();

            } catch (jsonError) {

                data = {};
            }


            /* ========================================
               GUEST
            ======================================== */

            if (response.status === 401) {

                setText(
                    usernameElement,
                    "مهمان"
                );

                setText(
                    emailElement,
                    "برای استفاده از امکانات حساب وارد شوید."
                );

                setText(
                    avatarElement,
                    "👤"
                );

                setStatus(
                    "مهمان",
                    "#f3f4f6",
                    "#4b5563"
                );


                if (accountContentElement) {

                    accountContentElement.innerHTML = `

                        <div class="card guest">

                            <div class="guest-icon">
                                👤
                            </div>

                            <h2>
                                شما به عنوان مهمان وارد Brain شده‌اید
                            </h2>

                            <p>
                                مهمان‌ها روزانه ۱۰ پیام دریافت می‌کنند.
                            </p>

                            <br>

                            <a
                                href="/login/"
                                class="button">
                                ورود به حساب
                            </a>

                            <a
                                href="/register/"
                                class="button button-light">
                                ثبت‌نام
                            </a>

                        </div>


                        <div class="card">

                            <h2>
                                📊 مصرف روزانه
                            </h2>

                            <p class="card-description">
                                محدودیت مهمان
                            </p>

                            <div class="usage-number">
                                ۱۰ پیام
                            </div>

                        </div>

                    `;
                }

                return;
            }


            /* ========================================
               OTHER ERRORS
            ======================================== */

            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "خطا در دریافت اطلاعات حساب"
                );
            }


            /* ========================================
               AUTHENTICATED USER
            ======================================== */

            const user =
                data.user || {};

            const usage =
                data.usage || {};


            const username =
                user.username ||
                "کاربر";


            setText(
                usernameElement,
                username
            );

            setText(
                emailElement,
                user.email ||
                "ایمیل ثبت نشده"
            );

            setText(
                avatarElement,
                getInitial(username)
            );

            setStatus(
                "حساب فعال",
                "#ecfdf5",
                "#047857"
            );


            setText(
                profileUsernameElement,
                username
            );

            setText(
                profileEmailElement,
                user.email ||
                "ثبت نشده"
            );

            setText(
                profileIdElement,
                user.id ??
                "—"
            );


            /* ========================================
               USAGE
            ======================================== */

            const dailyMessages =
                Number(
                    usage.daily_messages || 0
                );


            const limit =
                usage.limit;


            if (limit === null) {

                setText(
                    usageNumberElement,
                    "نامحدود"
                );

                setText(
                    usageUsedElement,
                    `${dailyMessages} پیام استفاده شده`
                );

                setText(
                    usageLimitElement,
                    "نامحدود"
                );

                if (usageProgressElement) {

                    usageProgressElement.style.width =
                        "0%";
                }

            } else {

                const numericLimit =
                    Number(limit || 0);

                const remaining =
                    usage.remaining ??
                    Math.max(
                        numericLimit -
                        dailyMessages,
                        0
                    );


                let percentage = 0;

                if (numericLimit > 0) {

                    percentage =
                        Math.min(
                            (
                                dailyMessages /
                                numericLimit
                            ) * 100,
                            100
                        );
                }


                setText(
                    usageNumberElement,
                    `${remaining} پیام باقی‌مانده`
                );

                setText(
                    usageUsedElement,
                    `${dailyMessages} استفاده شده`
                );

                setText(
                    usageLimitElement,
                    `از ${numericLimit}`
                );


                if (usageProgressElement) {

                    usageProgressElement.style.width =
                        `${percentage}%`;
                }
            }


            /* ========================================
               SUBSCRIPTION
            ======================================== */

            setText(
                subscriptionPlanElement,
                usage.plan ||
                "رایگان"
            );

        } catch (error) {

            console.error(
                "Account error:",
                error
            );


            setText(
                usernameElement,
                "خطا"
            );

            setText(
                emailElement,
                error.message ||
                "خطا در دریافت اطلاعات حساب"
            );

            setStatus(
                "خطا",
                "#fef2f2",
                "#b91c1c"
            );
        }
    }


    /* ========================================
       LOGOUT
    ======================================== */

    async function logoutUser() {

        if (!logoutButton) {
            return;
        }


        const originalText =
            logoutButton.textContent;


        logoutButton.disabled =
            true;

        logoutButton.textContent =
            "در حال خروج...";


        try {

            const response =
                await fetch(
                    "/api/auth/logout/",
                    {
                        method: "POST",
                        credentials: "same-origin",
                        headers: {
                            "Accept": "application/json"
                        }
                    }
                );


            let data = {};

            try {

                data =
                    await response.json();

            } catch (jsonError) {

                data = {};
            }


            if (response.ok) {

                window.location.href =
                    "/";

                return;
            }


            throw new Error(
                data.error ||
                "خروج از حساب انجام نشد."
            );

        } catch (error) {

            console.error(
                "Logout error:",
                error
            );


            alert(
                error.message ||
                "خروج از حساب انجام نشد."
            );


            logoutButton.disabled =
                false;

            logoutButton.textContent =
                originalText;
        }
    }


    /* ========================================
       EVENTS
    ======================================== */

    if (logoutButton) {

        logoutButton.addEventListener(
            "click",
            logoutUser
        );
    }


    /* ========================================
       INITIALIZE
    ======================================== */

    loadAccount();

});