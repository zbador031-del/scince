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

    const tickers = document.querySelectorAll(
        ".honor-ticker__content, .admin-honor-content"
    );

    tickers.forEach((track) => {
        const windowElement = track.parentElement;
        const groupSelector = track.classList.contains(
            "admin-honor-content"
        )
            ? ".admin-honor-group"
            : ".honor-ticker__group";
        const firstGroup = track.querySelector(groupSelector);

        if (!windowElement || !firstGroup) {
            return;
        }

        const fillTrack = () => {
            const groupWidth = firstGroup.getBoundingClientRect().width;
            const requiredWidth = windowElement.clientWidth + groupWidth;
            let safetyCounter = 0;

            while (
                track.scrollWidth < requiredWidth
                && safetyCounter < 20
            ) {
                const clone = firstGroup.cloneNode(true);
                clone.setAttribute("aria-hidden", "true");
                track.appendChild(clone);
                safetyCounter += 1;
            }

            return groupWidth;
        };

        let loopWidth = fillTrack();
        let offset = 0;
        let previousTime = performance.now();
        const speed = window.matchMedia("(max-width: 700px)").matches
            ? 58
            : 68;

        track.dataset.tickerRunning = "true";

        const animateTicker = (currentTime) => {
            const elapsedSeconds = Math.min(
                (currentTime - previousTime) / 1000,
                0.1
            );
            previousTime = currentTime;
            offset -= speed * elapsedSeconds;

            if (loopWidth > 0 && Math.abs(offset) >= loopWidth) {
                offset += loopWidth;
            }

            track.style.transform = `translate3d(${offset}px, 0, 0)`;
            window.requestAnimationFrame(animateTicker);
        };

        window.addEventListener("resize", () => {
            loopWidth = fillTrack();
        });

        document.addEventListener("visibilitychange", () => {
            previousTime = performance.now();
        });

        window.requestAnimationFrame(animateTicker);
    });
});
