document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".analysis-form");
    const button = document.querySelector(".submit-btn");

    if (form && button) {
        form.addEventListener("submit", () => {
            button.disabled = true;
            button.innerHTML = "Analyzing requirements <span>…</span>";
        });
    }
});
