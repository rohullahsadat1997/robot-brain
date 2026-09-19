let remainingMessages = null;


/* =========================================================
   UPDATE REMAINING MESSAGES
========================================================= */

function updateRemainingMessages(count) {

    remainingMessages = count;

    let counter =
        document.getElementById("remainingMessages");


    if (!counter) {

        counter = document.createElement("div");

        counter.id = "remainingMessages";

        counter.className = "remaining-messages";

        document.body.appendChild(counter);

    }


    if (
        count === null ||
        count === undefined
    ) {

        counter.textContent =
            "پیام‌های باقی‌مانده: نامحدود";

        return;

    }


    counter.textContent =
        `پیام‌های باقی‌مانده: ${count}`;

}


/* =========================================================
   VARIABLES
========================================================= */

let conversationId = null;

let mediaRecorder = null;

let audioChunks = [];

let isRecording = false;


/* =========================================================
   DOM ELEMENTS
========================================================= */

const messageInput =
    document.getElementById("messageInput");


const sendButton =
    document.getElementById("sendButton");


const messagesContainer =
    document.getElementById("messages");


const conversationList =
    document.getElementById("conversationList");


const newChatButton =
    document.getElementById("newChatButton");


const voiceButton =
    document.getElementById("voiceButton");


/* =========================================================
   ACCOUNT MENU ELEMENTS
========================================================= */

const accountMenu =
    document.getElementById("accountMenu");


const accountMenuButton =
    document.getElementById("accountMenuButton");


const accountDropdown =
    document.getElementById("accountDropdown");


const accountAvatar =
    document.getElementById("accountAvatar");


const accountName =
    document.getElementById("accountName");


const accountPlan =
    document.getElementById("accountPlan");


const dropdownAvatar =
    document.getElementById("dropdownAvatar");


const dropdownName =
    document.getElementById("dropdownName");


const dropdownEmail =
    document.getElementById("dropdownEmail");


const authenticatedMenu =
    document.getElementById("authenticatedMenu");


const guestMenu =
    document.getElementById("guestMenu");


const menuLogoutButton =
    document.getElementById("menuLogoutButton");


/* =========================================================
   ACCOUNT MENU
========================================================= */


/*
    باز و بسته کردن منوی حساب
*/

function toggleAccountMenu() {

    if (!accountMenu) {

        return;

    }


    const isOpen =
        accountMenu.classList.contains("open");


    if (isOpen) {

        closeAccountMenu();

    } else {

        openAccountMenu();

    }

}


/*
    باز کردن
*/

function openAccountMenu() {

    if (!accountMenu) {

        return;

    }


    accountMenu.classList.add("open");


    if (accountMenuButton) {

        accountMenuButton.setAttribute(
            "aria-expanded",
            "true"
        );

    }

}


/*
    بستن
*/

function closeAccountMenu() {

    if (!accountMenu) {

        return;

    }


    accountMenu.classList.remove("open");


    if (accountMenuButton) {

        accountMenuButton.setAttribute(
            "aria-expanded",
            "false"
        );

    }

}


/*
    کلیک روی Account
*/

if (accountMenuButton) {

    accountMenuButton.addEventListener(
        "click",
        function(event) {

            event.stopPropagation();

            toggleAccountMenu();

        }
    );

}


/*
    جلوگیری از بسته شدن هنگام کلیک
    داخل خود Dropdown
*/

if (accountDropdown) {

    accountDropdown.addEventListener(
        "click",
        function(event) {

            event.stopPropagation();

        }
    );

}


/*
    کلیک بیرون منو
*/

document.addEventListener(
    "click",
    function() {

        closeAccountMenu();

    }
);


/* =========================================================
   UPDATE ACCOUNT UI
========================================================= */

function updateAccountUI(data) {

    if (!data) {

        return;

    }


    /*
        =========================
        GUEST
        =========================
    */

    if (
        !data.authenticated ||
        !data.user
    ) {

        if (accountName) {

            accountName.textContent =
                "مهمان";

        }


        if (accountPlan) {

            accountPlan.textContent =
                "۱۰ پیام در روز";

        }


        if (dropdownName) {

            dropdownName.textContent =
                "مهمان";

        }


        if (dropdownEmail) {

            dropdownEmail.textContent =
                "وارد حساب نشده‌اید";

        }


        if (authenticatedMenu) {

            authenticatedMenu.style.display =
                "none";

        }


        if (guestMenu) {

            guestMenu.style.display =
                "flex";

        }


        return;

    }


    /*
        =========================
        AUTHENTICATED USER
        =========================
    */

    const user =
        data.user;


    if (accountName) {

        accountName.textContent =
            user.username || "کاربر";

    }


    if (dropdownName) {

        dropdownName.textContent =
            user.username || "کاربر";

    }


    if (dropdownEmail) {

        dropdownEmail.textContent =
            user.email || "ایمیل ثبت نشده";

    }


    /*
        برنامه / سهمیه
    */

    if (
        data.usage
    ) {

        const plan =
            data.usage.plan;


        const remaining =
            data.usage.remaining;


        if (plan === "premium") {

            if (accountPlan) {

                accountPlan.textContent =
                    "Premium";

            }

        } else if (plan === "admin") {

            if (accountPlan) {

                accountPlan.textContent =
                    "مدیر";

            }

        } else {

            if (
                remaining !== null &&
                remaining !== undefined
            ) {

                if (accountPlan) {

                    accountPlan.textContent =
                        `${remaining} پیام باقی‌مانده`;

                }

            } else {

                if (accountPlan) {

                    accountPlan.textContent =
                        "حساب کاربری";

                }

            }

        }


        /*
            بروزرسانی شمارنده اصلی
        */

        if (
            remaining !== null &&
            remaining !== undefined
        ) {

            updateRemainingMessages(
                remaining
            );

        }

    } else {

        if (accountPlan) {

            accountPlan.textContent =
                "حساب کاربری";

        }

    }


    /*
        نمایش منوی کاربر
    */

    if (authenticatedMenu) {

        authenticatedMenu.style.display =
            "flex";

    }


    if (guestMenu) {

        guestMenu.style.display =
            "none";

    }

}


/* =========================================================
   LOAD ACCOUNT STATUS
========================================================= */

async function loadAccountStatus() {

    try {

        /*
            اول API اصلی وضعیت ورود
        */

        const response =
            await fetch(
                "/api/auth/me/",
                {
                    method: "GET",

                    credentials: "same-origin",

                    cache: "no-store"
                }
            );


        const data =
            await response.json();


        /*
            وضعیت اولیه حساب
        */

        updateAccountUI(
            data
        );


        /*
            اگر کاربر لاگین بود،
            اطلاعات کامل Account را هم بگیر
        */

        if (
            data.authenticated &&
            data.user
        ) {

            try {

                const accountResponse =
                    await fetch(
                        "/api/auth/account/",
                        {
                            method: "GET",

                            credentials: "same-origin",

                            cache: "no-store"
                        }
                    );


                if (
                    accountResponse.ok
                ) {

                    const accountData =
                        await accountResponse.json();


                    updateAccountUI(
                        accountData
                    );

                }

            } catch (accountError) {

                console.error(
                    "Account API error:",
                    accountError
                );

            }

        }


    } catch (error) {

        console.error(
            "Load account status error:",
            error
        );


        /*
            اگر API در دسترس نبود،
            حساب را اشتباهاً لاگین‌شده نشان نده
        */

        updateAccountUI({
            authenticated: false,
            user: null
        });

    }

}


/* =========================================================
   LOGOUT
========================================================= */

async function logoutUser() {

    if (!menuLogoutButton) {

        return;

    }


    /*
        جلوگیری از چند کلیک
    */

    menuLogoutButton.disabled =
        true;


    try {

        const response =
            await fetch(
                "/api/auth/logout/",
                {
                    method: "POST",

                    credentials: "same-origin",

                    headers: {
                        "X-Requested-With":
                            "XMLHttpRequest"
                    }
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            console.error(
                "Logout failed:",
                data
            );


            alert(
                data.error ||
                "خروج از حساب انجام نشد."
            );


            return;

        }


        /*
            بستن منو
        */

        closeAccountMenu();


        /*
            پاک کردن وضعیت فعلی
        */

        updateAccountUI({
            authenticated: false,
            user: null
        });


        /*
            صفحه را دوباره بارگذاری می‌کنیم
            تا Session جدید کاملاً اعمال شود.
        */

        window.location.reload();


    } catch (error) {

        console.error(
            "Logout error:",
            error
        );


        alert(
            "خطایی هنگام خروج از حساب رخ داد."
        );


    } finally {

        menuLogoutButton.disabled =
            false;

    }

}


/*
    دکمه خروج داخل منوی Account
*/

if (menuLogoutButton) {

    menuLogoutButton.addEventListener(
        "click",
        logoutUser
    );

}


/* =========================================================
   FORMAT MESSAGE
========================================================= */

function formatMessage(text) {

    return text

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        )

        .replace(
            /\n/g,
            "<br>"
        );

}


/* =========================================================
   ADD MESSAGE
========================================================= */

function addMessage(
    role,
    text
) {

    const message =
        document.createElement("div");


    message.className =
        "message " + role;


    const bubble =
        document.createElement("div");


    bubble.className =
        "bubble";


    bubble.innerHTML =
        formatMessage(text);


    message.appendChild(
        bubble
    );


    messagesContainer.appendChild(
        message
    );


    messagesContainer.scrollTop =
        messagesContainer.scrollHeight;

}


/* =========================================================
   TYPING
========================================================= */

function addTypingMessage() {

    const message =
        document.createElement("div");


    message.className =
        "message assistant";


    message.id =
        "typingMessage";


    const bubble =
        document.createElement("div");


    bubble.className =
        "bubble typing";


    bubble.textContent =
        "Brain در حال فکر کردن است...";


    message.appendChild(
        bubble
    );


    messagesContainer.appendChild(
        message
    );


    messagesContainer.scrollTop =
        messagesContainer.scrollHeight;

}


function removeTypingMessage() {

    const typingMessage =
        document.getElementById(
            "typingMessage"
        );


    if (typingMessage) {

        typingMessage.remove();

    }

}


/* =========================================================
   LOAD CONVERSATIONS
========================================================= */

async function loadConversations() {

    try {

        const response =
            await fetch(
                "/api/conversations/",
                {
                    credentials: "same-origin"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Failed to load conversations"
            );

        }


        renderConversations(
            data.conversations
        );


    } catch (error) {

        console.error(error);


        conversationList.innerHTML = `
            <div class="loading-conversations">
                خطا در بارگذاری گفتگوها
            </div>
        `;

    }

}


/* =========================================================
   RENDER CONVERSATIONS
========================================================= */

function renderConversations(
    conversations
) {

    conversationList.innerHTML =
        "";


    if (!conversations.length) {

        conversationList.innerHTML = `
            <div class="loading-conversations">
                هنوز گفتگویی وجود ندارد.
            </div>
        `;

        return;

    }


    conversations.forEach(
        conversation => {

            const item =
                document.createElement("div");


            item.className =
                "conversation-item";


            if (
                conversation.id ===
                conversationId
            ) {

                item.classList.add(
                    "active"
                );

            }


            item.dataset.id =
                conversation.id;


            item.innerHTML = `

                <div class="conversation-item-content">

                    <div class="conversation-item-title">
                        ${escapeHtml(
                            conversation.title
                        )}
                    </div>

                    <div class="conversation-item-preview">
                        ${escapeHtml(
                            conversation.preview ||
                            "گفتگوی جدید"
                        )}
                    </div>

                </div>

                <button
                    class="delete-conversation-btn"
                    title="حذف گفتگو"
                    type="button"
                >
                    🗑
                </button>

            `;


            /*
                باز کردن گفتگو
            */

            item
                .querySelector(
                    ".conversation-item-content"
                )
                .addEventListener(
                    "click",
                    function() {

                        openConversation(
                            conversation.id
                        );

                    }
                );


            /*
                حذف گفتگو
            */

            item
                .querySelector(
                    ".delete-conversation-btn"
                )
                .addEventListener(
                    "click",
                    function(event) {

                        event.stopPropagation();


                        deleteConversation(
                            conversation.id
                        );

                    }
                );


            conversationList.appendChild(
                item
            );

        }
    );

}


/* =========================================================
   DELETE CONVERSATION
========================================================= */

async function deleteConversation(
    id
) {

    const confirmed =
        confirm(
            "آیا مطمئن هستید که می‌خواهید این گفتگو را حذف کنید؟"
        );


    if (!confirmed) {

        return;

    }


    try {

        const response =
            await fetch(
                `/api/conversations/${id}/delete/`,
                {
                    method: "DELETE",

                    credentials: "same-origin"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            alert(
                data.error ||
                "حذف گفتگو انجام نشد."
            );

            return;

        }


        /*
            اگر همین گفتگوی فعلی حذف شده
        */

        if (
            conversationId === id
        ) {

            startNewChat();

        }


        /*
            بارگذاری مجدد لیست
        */

        loadConversations();


    } catch (error) {

        console.error(
            "Delete conversation error:",
            error
        );


        alert(
            "خطایی هنگام حذف گفتگو رخ داد."
        );

    }

}


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHtml(text) {

    const div =
        document.createElement("div");


    div.textContent =
        text || "";


    return div.innerHTML;

}


/* =========================================================
   OPEN CONVERSATION
========================================================= */

async function openConversation(
    id
) {

    try {

        conversationId =
            id;


        messagesContainer.innerHTML = `
            <div class="message assistant">
                <div class="bubble typing">
                    در حال بارگذاری گفتگو...
                </div>
            </div>
        `;


        await loadConversationFromServer(
            id
        );


        renderConversationsAfterSelection();


    } catch (error) {

        console.error(error);


        addMessage(
            "assistant",
            "خطا در باز کردن گفتگو."
        );

    }

}


/* =========================================================
   LOAD CONVERSATION
========================================================= */

async function loadConversationFromServer(
    id
) {

    const response =
        await fetch(
            `/api/conversations/${id}/`,
            {
                credentials: "same-origin"
            }
        );


    const data =
        await response.json();


    if (!response.ok) {

        throw new Error(
            data.error ||
            "Failed to load conversation"
        );

    }


    messagesContainer.innerHTML =
        "";


    if (!data.messages.length) {

        addMessage(
            "assistant",
            "این گفتگو هنوز پیامی ندارد."
        );

        return;

    }


    data.messages.forEach(
        message => {

            addMessage(
                message.role,
                message.content
            );

        }
    );


    messagesContainer.scrollTop =
        messagesContainer.scrollHeight;

}


/* =========================================================
   REFRESH ACTIVE ITEM
========================================================= */

function renderConversationsAfterSelection() {

    const items =
        document.querySelectorAll(
            ".conversation-item"
        );


    items.forEach(
        item => {

            const id =
                Number(
                    item.dataset.id
                );


            if (
                id === conversationId
            ) {

                item.classList.add(
                    "active"
                );

            } else {

                item.classList.remove(
                    "active"
                );

            }

        }
    );

}


/* =========================================================
   NEW CHAT
========================================================= */

function startNewChat() {

    conversationId =
        null;


    messagesContainer.innerHTML = `
        <div class="message assistant">

            <div class="bubble">

                <strong>
                    سلام 👋
                </strong>

                <br>

                من Brain هستم.

                <br>

                آماده‌ام با شما گفتگو کنم.

            </div>

        </div>
    `;


    renderConversationsAfterSelection();


    messageInput.value =
        "";


    messageInput.focus();

}


/* =========================================================
   SEND MESSAGE
========================================================= */

async function sendMessage() {

    const message =
        messageInput.value.trim();


    if (!message) {

        return;

    }


    addMessage(
        "user",
        message
    );


    messageInput.value =
        "";


    messageInput.style.height =
        "auto";


    sendButton.disabled =
        true;


    addTypingMessage();


    try {

        const body = {

            message:
                message

        };


        if (
            conversationId !== null
        ) {

            body.conversation_id =
                conversationId;

        }


        const response =
            await fetch(
                "/api/chat/",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    credentials: "same-origin",

                    body:
                        JSON.stringify(body)
                }
            );


        const data =
            await response.json();


        console.log(
            "CHAT API RESPONSE:",
            data
        );


        removeTypingMessage();


        if (!response.ok) {

            addMessage(
                "assistant",
                data.error ||
                "خطایی در ارتباط با Brain رخ داد."
            );


            console.error(data);


            return;

        }


        conversationId =
            data.conversation_id;


        /*
            تعداد پیام‌های باقی‌مانده
        */

        if (
            data.remaining_messages !== undefined
        ) {

            updateRemainingMessages(
                data.remaining_messages
            );

        }


        /*
            پاسخ Brain
        */

        addMessage(
            "assistant",
            data.assistant_message.content
        );


        /*
            بروزرسانی گفتگوها
        */

        await loadConversations();


        renderConversationsAfterSelection();


    } catch (error) {

        removeTypingMessage();


        addMessage(
            "assistant",
            "ارتباط با سرور برقرار نشد."
        );


        console.error(error);


    } finally {

        sendButton.disabled =
            false;


        messageInput.focus();

    }

}


/* =========================================================
   VOICE
========================================================= */

async function toggleVoiceRecording() {

    if (isRecording) {

        stopVoiceRecording();

    } else {

        await startVoiceRecording();

    }

}


/* =========================================================
   START RECORDING
========================================================= */

async function startVoiceRecording() {

    try {

        if (
            !navigator.mediaDevices ||
            !navigator.mediaDevices.getUserMedia
        ) {

            addMessage(
                "assistant",
                "مرورگر شما از ضبط صدا پشتیبانی نمی‌کند."
            );

            return;

        }


        const stream =
            await navigator.mediaDevices.getUserMedia({
                audio: true
            });


        audioChunks =
            [];


        mediaRecorder =
            new MediaRecorder(
                stream
            );


        mediaRecorder.addEventListener(
            "dataavailable",
            function(event) {

                if (
                    event.data.size > 0
                ) {

                    audioChunks.push(
                        event.data
                    );

                }

            }
        );


        mediaRecorder.addEventListener(
            "stop",
            function() {

                stream
                    .getTracks()
                    .forEach(
                        track =>
                            track.stop()
                    );


                sendRecordedAudio();

            }
        );


        mediaRecorder.start();


        isRecording =
            true;


        voiceButton.classList.add(
            "recording"
        );


        voiceButton.textContent =
            "⏹️";


        voiceButton.title =
            "توقف ضبط";


        messageInput.placeholder =
            "در حال ضبط صدا...";


    } catch (error) {

        console.error(error);


        addMessage(
            "assistant",
            "دسترسی به میکروفون داده نشد."
        );

    }

}


/* =========================================================
   STOP RECORDING
========================================================= */

function stopVoiceRecording() {

    if (!mediaRecorder) {

        return;

    }


    if (
        mediaRecorder.state ===
        "recording"
    ) {

        mediaRecorder.stop();

    }


    isRecording =
        false;


    voiceButton.classList.remove(
        "recording"
    );


    voiceButton.textContent =
        "🎙️";


    voiceButton.title =
        "ضبط صدا";


    messageInput.placeholder =
        "پیام خود را بنویسید...";

}


/* =========================================================
   SEND RECORDED AUDIO
========================================================= */

async function sendRecordedAudio() {

    if (!audioChunks.length) {

        return;

    }


    const audioBlob =
        new Blob(
            audioChunks,
            {
                type:
                    mediaRecorder.mimeType ||
                    "audio/webm"
            }
        );


    const formData =
        new FormData();


    formData.append(
        "audio",
        audioBlob,
        "voice.webm"
    );


    /*
        ارسال conversation_id
    */

    if (
        conversationId !== null
    ) {

        formData.append(
            "conversation_id",
            conversationId
        );

    }


    /*
        پیام صوتی کاربر
    */

    addMessage(
        "user",
        "🎙️ پیام صوتی"
    );


    /*
        حالت پردازش
    */

    addTypingMessage();


    voiceButton.disabled =
        true;


    try {

        const response =
            await fetch(
                "/api/voice-test/",
                {
                    method: "POST",

                    credentials: "same-origin",

                    body: formData
                }
            );


        const data =
            await response.json();


        /*
            حذف typing
        */

        removeTypingMessage();


        /*
            بررسی خطا
        */

        if (!response.ok) {

            addMessage(
                "assistant",
                data.error ||
                "خطایی در پردازش صدا رخ داد."
            );


            console.error(
                "VOICE ERROR:",
                data
            );


            return;

        }


        /*
            ذخیره conversation
        */

        conversationId =
            data.conversation_id;


        /*
            تعداد پیام‌های باقی‌مانده
        */

        if (
            data.remaining_messages !== undefined
        ) {

            updateRemainingMessages(
                data.remaining_messages
            );

        }


        /*
            متن تشخیص داده شده
        */

        if (
            data.transcript
        ) {

            addMessage(
                "user",
                data.transcript
            );

        }


        /*
            پاسخ Brain
        */

        if (
            data.assistant_message &&
            data.assistant_message.content
        ) {

            addMessage(
                "assistant",
                data.assistant_message.content
            );

        }


        /*
            بروزرسانی گفتگوها
        */

        await loadConversations();


        renderConversationsAfterSelection();


    } catch (error) {

        removeTypingMessage();


        console.error(
            "VOICE REQUEST ERROR:",
            error
        );


        addMessage(
            "assistant",
            "ارتباط با سرور برقرار نشد."
        );


    } finally {

        voiceButton.disabled =
            false;


        audioChunks =
            [];

    }

}


/* =========================================================
   EVENTS
========================================================= */

if (sendButton) {

    sendButton.addEventListener(
        "click",
        sendMessage
    );

}


if (newChatButton) {

    newChatButton.addEventListener(
        "click",
        startNewChat
    );

}


if (voiceButton) {

    voiceButton.addEventListener(
        "click",
        toggleVoiceRecording
    );

}


if (messageInput) {

    messageInput.addEventListener(
        "keydown",
        function(event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();


                sendMessage();

            }

        }
    );


    messageInput.addEventListener(
        "input",
        function() {

            this.style.height =
                "auto";


            this.style.height =
                Math.min(
                    this.scrollHeight,
                    140
                ) + "px";

        }
    );

}


/* =========================================================
   SIDEBAR TOGGLE
========================================================= */

const sidebarToggle =
    document.getElementById(
        "sidebarToggle"
    );


const appContainer =
    document.querySelector(
        ".app-container"
    );


if (
    sidebarToggle &&
    appContainer
) {

    sidebarToggle.addEventListener(
        "click",
        () => {

            appContainer.classList.toggle(
                "sidebar-collapsed"
            );

        }
    );

}


/* =========================================================
   INITIAL LOAD
========================================================= */

async function initializeBrain() {

    /*
        اول وضعیت واقعی حساب را بخوان
    */

    await loadAccountStatus();


    /*
        سپس گفتگوها را بارگذاری کن
    */

    await loadConversations();


    /*
        در نهایت روی Input تمرکز کن
    */

    if (messageInput) {

        messageInput.focus();

    }

}


/*
    شروع برنامه
*/

initializeBrain();