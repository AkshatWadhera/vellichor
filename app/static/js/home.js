const menuButtons = document.querySelectorAll(".workspace-menu-btn");

menuButtons.forEach((button) => {

    button.addEventListener("click", (event) => {

        event.preventDefault();
        event.stopPropagation();

        const dropdown = button.nextElementSibling;

        document.querySelectorAll(".workspace-dropdown").forEach(menu => {

            if(menu !== dropdown){

                menu.classList.remove("active");

            }

        });

        dropdown.classList.toggle("active");

    });

});

document.addEventListener("click", () => {

    document.querySelectorAll(".workspace-dropdown").forEach(menu => {

        menu.classList.remove("active");

    });

});


function postAction(conversationId, action, data = {}) {

    const form = document.createElement("form");

    form.method = "POST";
    form.action = `/${conversationId}/${action}`;

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
document.querySelectorAll(".rename-btn").forEach(button => {

    button.addEventListener("click", (event) => {

        event.preventDefault();
        event.stopPropagation();

        const card = button.closest(".workspace-card");

        const conversationId = card.dataset.conversationId;

        const currentTitle = card.querySelector(".workspace-title-small").textContent.trim();

        const newTitle = prompt("Rename conversation", currentTitle);

        if (!newTitle || newTitle.trim() === currentTitle) return;

        postAction(conversationId, "rename", {
            title: newTitle.trim()
        });

    });

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


// Delete Convo
document.querySelectorAll(".delete-btn").forEach(button => {

    button.addEventListener("click", (event) => {

        event.preventDefault();
        event.stopPropagation();

        const conversationId =
            button.closest(".workspace-card").dataset.conversationId;

        const confirmed = confirm(
            "Delete this conversation permanently?"
        );

        if (!confirmed) return;

        postAction(conversationId, "delete");

    });

});


//Uplaod PDF
const uploadSurface = document.querySelector(".upload-surface");
const pdfInput = document.querySelector("#pdf-input");

if (uploadSurface && pdfInput) {

    uploadSurface.addEventListener("click", () => {

        pdfInput.click();

    });

    pdfInput.addEventListener("change", () => {

        if (pdfInput.files.length > 0) {

            uploadSurface.submit();

        }

    });

}


/* ========================================
   COMPOSER
======================================== */
const messagesContainer = document.querySelector(".messages");
const composerForm = document.querySelector("#composer-form");
const composerInput = document.querySelector("#composer-input");

function appendMessage(role, content) {

    const message = document.createElement("div");

    message.className = `message ${role}`;

    let body;

    if (role === "user") {

        const bubble = document.createElement("div");

        bubble.className = "message-bubble";

        body = document.createElement("div");

        body.className = "message-content";

        body.textContent = content;

        bubble.appendChild(body);

        message.appendChild(bubble);

    }

    else {

        body = document.createElement("div");

        body.className = "message-content";

        body.textContent = content;

        message.appendChild(body);

    }

    messagesContainer.appendChild(message);

    message.scrollIntoView({

        behavior: "smooth",
        block: "end"

    });

    return body;

}


if (composerForm && composerInput) {

    composerInput.addEventListener("keydown", (event) => {

    console.log(event.key);

    if (event.key === "Enter" && !event.shiftKey) {

        console.log("ENTER DETECTED");

        event.preventDefault();

        composerForm.requestSubmit();

    }

});

}


if (composerForm) {

    composerForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        const text = composerInput.value.trim();

        if (!text) return;

        appendMessage("user", text);

        composerInput.value = "";

        const formData = new FormData();

        formData.append("message", text);

        const response = await fetch(composerForm.action, {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        appendMessage("assistant", data.assistant);

    });

}