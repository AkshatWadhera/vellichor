const landingPage =
    document.querySelector(".landing-page");

const landingIntro =
    document.querySelector(".landing-intro");

const introState =
    document.querySelector(".intro-state");

const loginState =
    document.querySelector(".login-state");

const registerState =
    document.querySelector(".register-state");

const shutter =
    document.querySelector(".state-shutter");

const stateTriggers =
    document.querySelectorAll("[data-landing-state]");


let currentState = "intro";
let isTransitioning = false;


// =========================================================
// INITIAL STATE
// =========================================================

const initialState =
    landingPage.dataset.initialState || "intro";


if (initialState === "login") {

    introState.classList.remove("active");
    loginState.classList.add("active");

    currentState = "login";

}

else if (initialState === "register") {

    introState.classList.remove("active");
    registerState.classList.add("active");

    currentState = "register";

}


// =========================================================
// STATE TRANSITION
// =========================================================

function transitionTo(targetState) {

    // Do nothing if already in this state
    // or another transition is running.
    if (
        isTransitioning ||
        currentState === targetState
    ) {
        return;
    }

    isTransitioning = true;


    // -----------------------------------------------------
    // 1. Tiny physical compression
    // -----------------------------------------------------

    landingIntro.classList.add("mechanical-press");


    // -----------------------------------------------------
    // 2. Begin shutter transition
    // -----------------------------------------------------

    setTimeout(() => {

        landingIntro.classList.remove("mechanical-press");
        landingIntro.classList.add("transitioning");

    }, 75);


    // -----------------------------------------------------
    // 3. Close shutter
    // -----------------------------------------------------

    setTimeout(() => {

        shutter.classList.add("closed");

    }, 125);


    // -----------------------------------------------------
    // 4. Swap state while hidden
    // -----------------------------------------------------

    setTimeout(() => {

        introState.classList.remove("active");
        loginState.classList.remove("active");
        registerState.classList.remove("active");


        if (targetState === "intro") {

            introState.classList.add("active");

        }

        else if (targetState === "login") {

            loginState.classList.add("active");

        }

        else if (targetState === "register") {

            registerState.classList.add("active");

        }


        currentState = targetState;

    }, 300);


    // -----------------------------------------------------
    // 5. Open shutter
    // -----------------------------------------------------

    setTimeout(() => {

        shutter.classList.remove("closed");

    }, 390);


    // -----------------------------------------------------
    // 6. Finish transition
    // -----------------------------------------------------

    setTimeout(() => {

        landingIntro.classList.remove("transitioning");

        isTransitioning = false;

    }, 760);
}


// =========================================================
// STATE TRIGGERS
// =========================================================

stateTriggers.forEach((trigger) => {

    trigger.addEventListener("click", (event) => {

        event.preventDefault();

        const targetState =
            trigger.dataset.landingState;

        transitionTo(targetState);

    });

});