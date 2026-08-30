// ========================================
// WORKSPACE MENU DROPDOWNS
// Find all workspace menu buttons so we can
// attach click behavior to each one.
// ========================================
const menuButtons = document.querySelectorAll(".workspace-menu-btn");

menuButtons.forEach((button) => {

    button.addEventListener("click", (event) => {

        event.preventDefault();
        event.stopPropagation();

        const dropdown = button.nextElementSibling;

        //Clsoe all the dropdowns except the one that i just clicked
        document.querySelectorAll(".workspace-dropdown").forEach(menu => {

            if(menu !== dropdown){

                menu.classList.remove("active");

            }

        });

        //Open or Close the dropdown i clicked on
        dropdown.classList.toggle("active");

    });

});


//Close the dropdown whenever user clicks anywhere on the page
document.addEventListener("click", () => {

    document.querySelectorAll(".workspace-dropdown").forEach(menu => {

        menu.classList.remove("active");

    });

});




// ========================================
// POST ACTION HELPER
// Dynamically creates a hidden HTML form
// and submits conversation actions such as
// rename, pin, and delete to the Flask backend.
// ========================================
function postAction(conversationId, action, data = {}) {

    const form = document.createElement("form");

    form.method = "POST";
    form.action = `/${conversationId}/${action}`;

    // Add any extra action data as hidden
    // form inputs so Flask can receive it.
    Object.entries(data).forEach(([key, value]) => {

        const input = document.createElement("input");

        input.type = "hidden";
        input.name = key;
        input.value = value;

        form.appendChild(input);

    });

    document.body.appendChild(form);

    console.log(form.action);
    form.submit();
}


// Rename Convo
// ========================================
// RENAME CONVERSATION
// ========================================

const renameModal =
    document.querySelector("#rename-modal");

const renameForm =
    document.querySelector("#rename-form");

const renameInput =
    document.querySelector("#rename-input");

const renameCancel =
    document.querySelector("#rename-cancel");

let renameConversationId = null;
let renameCurrentTitle = "";


// Open Rename Modal
document.querySelectorAll(".rename-btn").forEach(button => {

    button.addEventListener("click", (event) => {

        event.preventDefault();
        event.stopPropagation();


        const card =
            button.closest(".workspace-card");


        renameConversationId =
            card.dataset.conversationId;


        renameCurrentTitle =
            card
                .querySelector(".workspace-title-small")
                .textContent
                .trim();


        renameInput.value =
            renameCurrentTitle;


        renameModal.classList.add("active");


        renameModal.classList.add("active");

        setTimeout(() => {

            renameInput.focus();
            renameInput.select();

        }, 50);

    });

});


// Cancel Rename
renameCancel.addEventListener("click", () => {

    renameModal.classList.remove("active");

    renameConversationId = null;

});


// Submit Rename
renameForm.addEventListener("submit", (event) => {

    event.preventDefault();


    const newTitle =
        renameInput.value.trim();


    // Nothing entered
    if (!newTitle){
        renameModal.classList.remove("active");
        return;
    }


    // Same title
    if (newTitle === renameCurrentTitle) {

        renameModal.classList.remove("active");

        return;

    }


    postAction(
        renameConversationId,
        "rename",
        {
            title: newTitle
        }
    );

});


// Pin and Unpin Convo
document.querySelectorAll(".pin-btn").forEach(button => {

    button.addEventListener("click", (event) => {

        event.preventDefault();
        event.stopPropagation();

        const conversationId =
            button.closest(".workspace-card").dataset.conversationId;

        postAction(conversationId, "pin");

    });

});


// ========================================
// DELETE CONVERSATION
// ========================================

const deleteModal =
    document.querySelector("#delete-modal");

const deleteCancel =
    document.querySelector("#delete-cancel");

const deleteConfirm =
    document.querySelector("#delete-confirm");

const deleteConversationName =
    document.querySelector("#delete-conversation-name");

let deleteConversationId = null;


// Open Delete Modal
document.querySelectorAll(".delete-btn").forEach(button => {

    button.addEventListener("click", (event) => {

        event.preventDefault();
        event.stopPropagation();


        const card =
            button.closest(".workspace-card");


        deleteConversationId =
            card.dataset.conversationId;


        const conversationTitle =
            card
                .querySelector(".workspace-title-small")
                .textContent
                .trim();


        deleteConversationName.textContent =
            conversationTitle;
       

        deleteModal.classList.add("active");

    });

});


// Cancel Delete
deleteCancel.addEventListener("click", () => {

    deleteModal.classList.remove("active");

    deleteConversationId = null;

});


// Confirm Delete
deleteConfirm.addEventListener("click", (event) => {

    event.preventDefault();
    event.stopPropagation();


    console.log(
        "Delete confirmed:",
        deleteConversationId
    );


    if (!deleteConversationId) {

        console.error(
            "No conversation ID available for deletion."
        );

        return;
    }


    postAction(
        deleteConversationId,
        "delete"
    );

});


// ========================================
// PDF UPLOAD
// ========================================

const uploadSurface = document.querySelector(".upload-surface");
const pdfInput = document.querySelector("#pdf-input");

function resetUploadState() {

    uploadSurface.classList.remove(
        "uploading",
        "upload-complete",
        "upload-error-state"
    );

}

if (uploadSurface && pdfInput) {

    uploadSurface.addEventListener("click", () => {

        if (
            uploadSurface.classList.contains("uploading") ||
            uploadSurface.classList.contains("upload-complete")
        ) {
            return;
        }

        pdfInput.click();

    });


    pdfInput.addEventListener("change", async () => {

        if (pdfInput.files.length === 0) return;

        resetUploadState();

        uploadSurface.classList.add("uploading");
        
        

        // Create FormData from the upload form
        const formData = new FormData(uploadSurface);


        try {

            const response = await fetch(
                uploadSurface.action,
                {
                    method: "POST",
                    body: formData
                }
            );


            const data = await response.json();


            if (data.success) {

                resetUploadState();

                uploadSurface.classList.add(
                    "upload-complete"
                );


                setTimeout(() => {

                    window.location.href =
                        `/chat/${data.conversation_id}`;

                }, 1200);

            }

            else {

                const errorMessages = {

                    NO_FILE:
                        "Please select a PDF before uploading.",

                    INVALID_EXTENSION:
                        "Vellichor only accepts PDF documents. Please upload a PDF document.",

                    INVALID_MIME:
                        "This file doesn't appear to be a valid PDF. Try again.",

                    PASSWORD_PROTECTED:
                        "This PDF is password-protected. Please upload an unlocked PDF.",

                    NO_TEXT:
                        "We couldn't find selectable text in this PDF. Please upload a text-based document.",

                    FILE_TOO_LARGE:
                        "This PDF is too large. Please upload a PDF smaller than 16 MB.",

                    PROCESSING_FAILED:
                        "Something went wrong while preparing your document. Please try again."

                };


                const errorMessage =
                    errorMessages[data.error_code]
                    || errorMessages.PROCESSING_FAILED;


                const errorMessageElement =
                    document.querySelector("#upload-error-message");


                if (errorMessageElement) {

                    errorMessageElement.textContent =
                        errorMessage;

                }


                resetUploadState();

                uploadSurface.classList.add("upload-error-state");

            }

        }

        catch (error) {

            console.error(
                "Upload request failed:",
                error
            );

        }

    });

}

/* ========================================
   COMPOSER
======================================== */

const messagesContainer =
    document.querySelector(".messages");

const composerForm =
    document.querySelector("#composer-form");

const composerInput =
    document.querySelector("#composer-input");

const composerSubmitButton =
    composerForm?.querySelector('button[type="submit"]');

/* ========================================
   MARKDOWN RENDERING
======================================== */

const md = markdownit({

    html: false,

    breaks: false,

    linkify: true

});


function renderMarkdown(content) {

    const rendered =
        md.render(content);

    return rendered.replace(
        /&lt;br\s*\/?&gt;/gi,
        "<br>"
    );

}


/* ========================================
   RENDER EXISTING MESSAGES
======================================== */

document
    .querySelectorAll(".message-markdown")
    .forEach((scriptElement) => {

        const markdown = JSON.parse(
            scriptElement.textContent
        );

        const messageContent =
            scriptElement
                .closest(".message")
                .querySelector(".message-content");

        messageContent.innerHTML =
            renderMarkdown(markdown);

        scriptElement.remove();

    });


    /* ========================================
   SCROLL CHAT TO BOTTOM
======================================== */

/* ========================================
   INITIAL CHAT POSITION
======================================== */

function scrollChatToBottom() {

    if (!messagesContainer) return;

    const startPosition =
        messagesContainer.scrollTop;

    const targetPosition =
        messagesContainer.scrollHeight -
        messagesContainer.clientHeight;

    const distance =
        targetPosition - startPosition;

    const duration = 750;

    const startTime = performance.now();


    function animateScroll(currentTime) {

        const elapsed =
            currentTime - startTime;

        const progress =
            Math.min(elapsed / duration, 1);


        /*
         * Ease-out curve.
         *
         * Starts gently,
         * moves faster through the middle,
         * then slows naturally at the bottom.
         */
        const eased =
            1 - Math.pow(1 - progress, 3);


        messagesContainer.scrollTop =
            startPosition +
            distance * eased;


        if (progress < 1) {

            requestAnimationFrame(
                animateScroll
            );

        }

    }


    requestAnimationFrame(
        animateScroll
    );

}


/*
 * Wait one browser frame so the
 * Markdown-rendered content has
 * its final layout height.
 */
requestAnimationFrame(() => {

    scrollChatToBottom();

});


/* ========================================
   APPEND MESSAGE
======================================== */

function appendMessage(role, content) {

    const message =
        document.createElement("div");

    message.className =
        `message ${role}`;

    let body;


    if (role === "user") {

        const bubble =
            document.createElement("div");

        bubble.className =
            "message-bubble";

        body =
            document.createElement("div");

        body.className =
            "message-content";

        body.innerHTML =
            renderMarkdown(content);

        bubble.appendChild(body);

        message.appendChild(bubble);

    }

    else {

        body =
            document.createElement("div");

        body.className =
            "message-content";

        body.innerHTML =
            renderMarkdown(content);

        message.appendChild(body);

    }


    messagesContainer.appendChild(message);


    messagesContainer.scrollTo({

        top: messagesContainer.scrollHeight,

        behavior: "smooth"

    });


    return body;

}


/* ========================================
   ENTER KEY
======================================== */

if (composerForm && composerInput) {

    composerInput.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                composerForm.requestSubmit();

            }

        }
    );

}


/* ========================================
   THINKING MESSAGE
======================================== */

function appendThinkingMessage() {

    const message =
        document.createElement("div");

    message.className =
        "message assistant thinking-message";


    const body =
        document.createElement("div");

    body.className =
        "message-content";


    body.innerHTML = `
        <div class="thinking-indicator">

            <span class="thinking-orbit orbit-one"></span>
            <span class="thinking-orbit orbit-two"></span>
            <span class="thinking-orbit orbit-three"></span>

            <span class="thinking-core">✦</span>

        </div>
    `;


    message.appendChild(body);

    messagesContainer.appendChild(message);


    messagesContainer.scrollTo({

        top: messagesContainer.scrollHeight,

        behavior: "smooth"

    });


    return message;

}


/* ========================================
   SEND MESSAGE
======================================== */

if (composerForm) {

    composerForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();


            const text =
                composerInput.value.trim();


            if (!text) return;

            composerSubmitButton.disabled = true;

            appendMessage(
                "user",
                text
            );


            composerInput.value = "";


            const thinkingMessage =
                appendThinkingMessage();

            const thinkingStartedAt =
                Date.now();


            const formData =
                new FormData();

            formData.append(
                "message",
                text
            );


            try {

                const response =
                    await fetch(
                        composerForm.action,
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                const data =
                    await response.json();


                /* ========================================
                   AI USAGE LIMIT
                ======================================== */

                if (
                    response.status === 429 &&
                    data.error_code === "AI_LIMIT_REACHED"
                ) {

                    const thinkingElapsed =
                        Date.now() - thinkingStartedAt;

                    const minimumThinkingTime =
                        1500;

                    const remainingThinkingTime =
                        Math.max(
                            0,
                            minimumThinkingTime - thinkingElapsed
                        );


                    if (remainingThinkingTime > 0) {

                        await new Promise(resolve => {

                            setTimeout(
                                resolve,
                                remainingThinkingTime
                            );

                        });

                    }


                    thinkingMessage.remove();


                    appendMessage(
                        "assistant",
                        "**A quiet moment for Vellichor.**\n\nToday's AI usage limit has been reached. Please come back a little later."
                    );


                    return;
                }


                /* ========================================
                   OTHER BACKEND ERRORS
                ======================================== */

                if (!response.ok) {

                    throw new Error(
                        data.error
                        || "Failed to generate AI response."
                    );

                }


                /* ========================================
                   MINIMUM THINKING TIME
                ======================================== */

                const thinkingElapsed =
                    Date.now() - thinkingStartedAt;


                const minimumThinkingTime =
                    2800;


                const remainingThinkingTime =
                    Math.max(
                        0,
                        minimumThinkingTime - thinkingElapsed
                    );


                if (remainingThinkingTime > 0) {

                    await new Promise(resolve => {

                        setTimeout(
                            resolve,
                            remainingThinkingTime
                        );

                    });

                }


                thinkingMessage.remove();


                appendMessage(
                    "assistant",
                    data.assistant
                );


            }

            catch (error) {

                console.error(
                    "Message request failed:",
                    error
                );


                thinkingMessage.remove();


                appendMessage(
                    "assistant",
                    "I couldn't complete that request right now. Please try again in a moment."
                );

            }

            finally {

                composerSubmitButton.disabled = false;

            }

        }
    );

}


// ========================================
// MOBILE SIDEBAR
// Mobile-only interaction
// ========================================

const mobileSidebarToggle =
    document.querySelector(".mobile-sidebar-toggle");

const mobileSidebarBackdrop =
    document.querySelector(".mobile-sidebar-backdrop");

const appShell =
    document.querySelector(".app-shell");


if (mobileSidebarToggle && appShell) {

    mobileSidebarToggle.addEventListener("click", () => {

        appShell.classList.toggle("sidebar-open");

    });

}


if (mobileSidebarBackdrop && appShell) {

    mobileSidebarBackdrop.addEventListener("click", () => {

        appShell.classList.remove("sidebar-open");

    });

}