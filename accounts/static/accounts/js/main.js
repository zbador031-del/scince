"use strict";


document.addEventListener("DOMContentLoaded", () => {
    const messages = document.querySelectorAll(".message");

    messages.forEach((message) => {
        window.setTimeout(() => {
            message.style.opacity = "0";
            message.style.transform = "translateY(-8px)";

            window.setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
});