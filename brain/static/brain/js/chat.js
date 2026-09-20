/* =========================================================
   BRAIN — CHAT PAGE
   V0.3.1
   Self-contained JavaScript
========================================================= */


/* =========================================================
   GLOBAL STATE
========================================================= */

let remainingMessages = null;

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

const sidebarToggle =
    document.getElementById("sidebarToggle");

const appContainer =
    document.querySelector(".app-container");


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
   UPDATE REMAINING MESSAGES
========================================================= */

function updateRemainingMessages(count) {

    remainingMessages = count;

    let counter =
        document.getElementById(
            "remainingMessages"
        );

    if (!counter) {

        counter =
            document.createElement("div");

        counter.id =
            "remainingMessages";

        counter.className =
            "remaining-messages";

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
   ACCOUNT MENU
========================================================= */

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


/* =========================================================
   ACCOUNT MENU EVENTS
========================================================= */

if (accountMenuButton) {

    accountMenuButton.addEventListener(
        "click",
        function(event) {

            event.preventDefault();

            event.stopPropagation();

            toggleAccountMenu();

        }
    );

}


if (accountDropdown) {

    accountDropdown.addEventListener(
        "click",
        function(event) {

            event.stopPropagation();

        }
    );

}


document.addEventListener(
    "click",
    function(event) {

        if (!accountMenu) {
            return;
        }

        if (
            !accountMenu.contains(
                event.target
            )
        ) {

            closeAccountMenu();

        }

    }
);


/* =========================================================
   UPDATE ACCOUNT UI
========================================================= */

function updateAccountUI(data) {

    if (!data) {
        return;
    }


    /* -----------------------------------------------------
       GUEST
    ----------------------------------------------------- */

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


    /* -----------------------------------------------------
       AUTHENTICATED USER
    ----------------------------------------------------- */

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
            user.email ||
            "ایمیل ثبت نشده";

    }


    /* -----------------------------------------------------
       PLAN / USAGE
    ----------------------------------------------------- */

    if (data.usage) {

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


    /* -----------------------------------------------------
       SHOW AUTHENTICATED MENU
    ----------------------------------------------------- */

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

        const response =
            await fetch(
                "/api/auth/me/",
                {
                    method: "GET",

                    credentials:
                        "same-origin",

                    cache:
                        "no-store"
                }
            );


        const data =
            await response.json();


        updateAccountUI(
            data
        );


        /* -------------------------------------------------
           LOAD FULL ACCOUNT DATA
        ------------------------------------------------- */

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

                            credentials:
                                "same-origin",

                            cache:
                                "no-store"
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


    menuLogoutButton.disabled =
        true;


    try {

        const response =
            await fetch(
                "/api/auth/logout/",
                {
                    method: "POST",

                    credentials:
                        "same-origin",

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


        closeAccountMenu();


        updateAccountUI({
            authenticated: false,
            user: null
        });


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

    if (
        text === null ||
        text === undefined
    ) {

        return "";

    }


    return String(text)

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

    if (!messagesContainer) {
        return;
    }


    const message =
        document.createElement("div");


    message.className =
        `message ${role}`;


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


    requestAnimationFrame(
        function() {

            messagesContainer.scrollTop =
                messagesContainer.scrollHeight;

        }
    );

}


/* =========================================================
   TYPING MESSAGE
========================================================= */

function addTypingMessage() {

    if (!messagesContainer) {
        return;
    }


    removeTypingMessage();


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

    if (!conversationList) {
        return;
    }


    try {

        const response =
            await fetch(
                "/api/conversations/",
                {
                    credentials:
                        "same-origin",

                    cache:
                        "no-store"
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
            data.conversations || []
        );


    } catch (error) {

        console.error(
            "Load conversations error:",
            error
        );


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

    if (!conversationList) {
        return;
    }


    conversationList.innerHTML =
        "";


    if (
        !conversations ||
        !conversations.length
    ) {

        conversationList.innerHTML = `
            <div class="loading-conversations">
                هنوز گفتگویی وجود ندارد.
            </div>
        `;

        return;

    }


    conversations.forEach(
        function(conversation) {

            const item =
                document.createElement("div");


            item.className =
                "conversation-item";


            if (
                Number(conversation.id) ===
                Number(conversationId)
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
                            conversation.title ||
                            "گفتگوی جدید"
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
                    aria-label="حذف گفتگو"
                    type="button"
                >
                    🗑
                </button>

            `;


            const content =
                item.querySelector(
                    ".conversation-item-content"
                );


            const deleteButton =
                item.querySelector(
                    ".delete-conversation-btn"
                );


            if (content) {

                content.addEventListener(
                    "click",
                    function() {

                        openConversation(
                            conversation.id
                        );

                    }
                );

            }


            if (deleteButton) {

                deleteButton.addEventListener(
                    "click",
                    function(event) {

                        event.preventDefault();

                        event.stopPropagation();


                        deleteConversation(
                            conversation.id
                        );

                    }
                );

            }


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

                    credentials:
                        "same-origin"
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


        if (
            Number(conversationId) ===
            Number(id)
        ) {

            startNewChat();

        }


        await loadConversations();


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

    if (!messagesContainer) {
        return;
    }


    try {

        conversationId =
            Number(id);


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


        closeMobileSidebar();

    } catch (error) {

        console.error(
            "Open conversation error:",
            error
        );


        removeTypingMessage();


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
                credentials:
                    "same-origin",

                cache:
                    "no-store"
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


    if (
        !data.messages ||
        !data.messages.length
    ) {

        addMessage(
            "assistant",
            "این گفتگو هنوز پیامی ندارد."
        );

        return;

    }


    data.messages.forEach(
        function(message) {

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
   REFRESH ACTIVE CONVERSATION
========================================================= */

function renderConversationsAfterSelection() {

    const items =
        document.querySelectorAll(
            ".conversation-item"
        );


    items.forEach(
        function(item) {

            const id =
                Number(
                    item.dataset.id
                );


            if (
                id ===
                Number(conversationId)
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


    if (messagesContainer) {

        messagesContainer.innerHTML = `
            <div class="welcome-screen">

                <div class="welcome-icon">
                    <img
                        src="/static/brain/images/brain-logo.jpg"
                        alt="Brain"
                    >
                </div>

                <h2>
                    سلام 👋
                </h2>

                <p>
                    من <strong>Brain</strong> هستم.
                </p>

                <span>
                    آماده‌ام با شما گفتگو کنم، فکر کنم و به شما کمک کنم.
                </span>

            </div>
        `;

    }


    renderConversationsAfterSelection();


    if (messageInput) {

        messageInput.value =
            "";

        messageInput.style.height =
            "auto";

    }


    closeMobileSidebar();


    if (messageInput) {

        messageInput.focus();

    }

}


/* =========================================================
   SEND MESSAGE
========================================================= */

async function sendMessage() {

    if (!messageInput) {
        return;
    }


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


    if (sendButton) {

        sendButton.disabled =
            true;

    }


    addTypingMessage();


    try {

        const body = {
            message: message
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

                    credentials:
                        "same-origin",

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


            console.error(
                data
            );


            return;

        }


        conversationId =
            data.conversation_id;


        if (
            data.remaining_messages !==
            undefined
        ) {

            updateRemainingMessages(
                data.remaining_messages
            );

        }


        if (
            data.assistant_message &&
            data.assistant_message.content
        ) {

            addMessage(
                "assistant",
                data.assistant_message.content
            );

        }


        await loadConversations();


        renderConversationsAfterSelection();


    } catch (error) {

        removeTypingMessage();


        console.error(
            "Send message error:",
            error
        );


        addMessage(
            "assistant",
            "ارتباط با سرور برقرار نشد."
        );


    } finally {

        if (sendButton) {

            sendButton.disabled =
                false;

        }


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

    if (!voiceButton) {
        return;
    }


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
                        function(track) {

                            track.stop();

                        }
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


        voiceButton.setAttribute(
            "aria-label",
            "توقف ضبط"
        );


        messageInput.placeholder =
            "در حال ضبط صدا...";


    } catch (error) {

        console.error(
            "Microphone error:",
            error
        );


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


    if (voiceButton) {

        voiceButton.classList.remove(
            "recording"
        );


        voiceButton.textContent =
            "🎙️";


        voiceButton.title =
            "ضبط صدا";


        voiceButton.setAttribute(
            "aria-label",
            "ضبط صدا"
        );

    }


    if (messageInput) {

        messageInput.placeholder =
            "پیام خود را بنویسید...";

    }

}


/* =========================================================
   SEND RECORDED AUDIO
========================================================= */

async function sendRecordedAudio() {

    if (!audioChunks.length) {
        return;
    }


    const mimeType =
        mediaRecorder &&
        mediaRecorder.mimeType
            ? mediaRecorder.mimeType
            : "audio/webm";


    const audioBlob =
        new Blob(
            audioChunks,
            {
                type: mimeType
            }
        );


    const formData =
        new FormData();


    formData.append(
        "audio",
        audioBlob,
        "voice.webm"
    );


    if (
        conversationId !== null
    ) {

        formData.append(
            "conversation_id",
            conversationId
        );

    }


    addMessage(
        "user",
        "🎙️ پیام صوتی"
    );


    addTypingMessage();


    if (voiceButton) {

        voiceButton.disabled =
            true;

    }


    try {

        const response =
            await fetch(
                "/api/voice-test/",
                {
                    method: "POST",

                    credentials:
                        "same-origin",

                    body:
                        formData
                }
            );


        const data =
            await response.json();


        removeTypingMessage();


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


        conversationId =
            data.conversation_id;


        if (
            data.remaining_messages !==
            undefined
        ) {

            updateRemainingMessages(
                data.remaining_messages
            );

        }


        if (
            data.transcript
        ) {

            addMessage(
                "user",
                data.transcript
            );

        }


        if (
            data.assistant_message &&
            data.assistant_message.content
        ) {

            addMessage(
                "assistant",
                data.assistant_message.content
            );

        }


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

        if (voiceButton) {

            voiceButton.disabled =
                false;

        }


        audioChunks =
            [];

    }

}


/* =========================================================
   SIDEBAR
========================================================= */

function toggleSidebar() {

    if (!appContainer) {
        return;
    }


    appContainer.classList.toggle(
        "sidebar-collapsed"
    );

}


function closeMobileSidebar() {

    if (!appContainer) {
        return;
    }


    if (
        window.innerWidth <= 768
    ) {

        appContainer.classList.add(
            "sidebar-collapsed"
        );

    }

}


function openMobileSidebar() {

    if (!appContainer) {
        return;
    }


    if (
        window.innerWidth <= 768
    ) {

        appContainer.classList.remove(
            "sidebar-collapsed"
        );

    }

}


if (
    sidebarToggle &&
    appContainer
) {

    sidebarToggle.addEventListener(
        "click",
        function(event) {

            event.preventDefault();

            event.stopPropagation();

            toggleSidebar();

        }
    );

}


/* =========================================================
   CLOSE MOBILE SIDEBAR WHEN CLICKING OUTSIDE
========================================================= */

document.addEventListener(
    "click",
    function(event) {

        if (!appContainer) {
            return;
        }


        if (
            window.innerWidth > 768
        ) {

            return;

        }


        if (
            appContainer.classList.contains(
                "sidebar-collapsed"
            )
        ) {

            return;

        }


        const sidebar =
            document.querySelector(
                ".sidebar"
            );


        if (!sidebar) {
            return;
        }


        if (
            sidebar.contains(
                event.target
            )
        ) {

            return;

        }


        if (
            sidebarToggle &&
            sidebarToggle.contains(
                event.target
            )
        ) {

            return;

        }


        closeMobileSidebar();

    }
);


/* =========================================================
   MOBILE RESIZE
========================================================= */

window.addEventListener(
    "resize",
    function() {

        if (!appContainer) {
            return;
        }


        /*
            وقتی از موبایل به دسکتاپ
            برمی‌گردیم، حالت موبایل
            Sidebar را پاک می‌کنیم.
        */

        if (
            window.innerWidth > 768
        ) {

            appContainer.classList.remove(
                "sidebar-collapsed"
            );

        }

    }
);


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


/* =========================================================
   MESSAGE INPUT
========================================================= */

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
                    window.innerWidth <= 768
                        ? 120
                        : 140
                ) + "px";

        }
    );

}


/* =========================================================
   INITIAL LOAD
========================================================= */

async function initializeBrain() {

    /*
        Account
    */

    await loadAccountStatus();


    /*
        Conversations
    */

    await loadConversations();


    /*
        Focus input
    */

    if (messageInput) {

        messageInput.focus();

    }

}


/* =========================================================
   START
========================================================= */

initializeBrain();