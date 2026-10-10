document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".analysis-form");
    const button = document.querySelector(".submit-btn");

    const scenarios = {
        banking: {
            project_name: "Secure Banking Platform", project_type: "Banking", team_size: 5,
            budget: "High", expected_users: "10,000–100,000", security_level: "Critical",
            scalability_need: "High", team_experience: "Intermediate", deadline: "Standard"
        },
        education: {
            project_name: "Smart Learning Platform", project_type: "Education", team_size: 4,
            budget: "Medium", expected_users: "10,000–100,000", security_level: "High",
            scalability_need: "High", team_experience: "Intermediate", deadline: "Standard"
        },
        commerce: {
            project_name: "NextGen E-Commerce", project_type: "E-Commerce", team_size: 8,
            budget: "High", expected_users: "100,000+", security_level: "High",
            scalability_need: "High", team_experience: "Advanced", deadline: "Standard"
        }
    };

    document.querySelectorAll("[data-scenario]").forEach(card => {
        card.addEventListener("click", () => {
            const data = scenarios[card.dataset.scenario];
            if (!form || !data) return;
            Object.entries(data).forEach(([name, value]) => {
                const field = form.elements[name];
                if (field) field.value = value;
            });
            form.scrollIntoView({ behavior: "smooth", block: "center" });
            document.querySelector(".analysis-form input[name='project_name']")?.focus();
        });
    });

    if (form && button) {
        form.addEventListener("submit", () => {
            button.disabled = true;
            button.innerHTML = "Analyzing requirements <span class='spinner'>◌</span>";
        });
    }

    document.querySelectorAll(".delete-record").forEach(button => {
        button.addEventListener("click", () => {
            if (!confirm("Delete this recommendation?")) return;
            const form = document.createElement("form");
            form.method = "POST";
            form.action = `/delete/${button.dataset.id}`;
            document.body.appendChild(form);
            form.submit();
        });
    });

    const compareForm = document.querySelector("#compare-form");
    if (compareForm) {
        compareForm.addEventListener("submit", (event) => {
            const selected = [...compareForm.querySelectorAll(".compare-check:checked")];
            if (selected.length < 2) {
                event.preventDefault();
                alert("Select at least 2 recommendations to compare.");
            } else if (selected.length > 3) {
                event.preventDefault();
                alert("Select a maximum of 3 recommendations.");
            }
        });
    }
});
