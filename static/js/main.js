// Placeholder for future features (dark mode toggle, etc.)
console.log("ToolifyHub loaded.");
// Dark/Light mode toggle
const btn = document.getElementById("themeToggle");
btn.addEventListener("click", () => {
    document.body.classList.toggle("light");
    btn.textContent = document.body.classList.contains("light") ? "☀️" : "🌙";
});
const toolNames = JSON.parse('{{ TOOLS | tojson }}').map(t => t.name);
const input = document.querySelector("input[name='q']");
const box = document.getElementById("suggestions");

input.addEventListener("input", () => {
    const value = input.value.toLowerCase();
    box.innerHTML = "";
    if (!value) return;

    const matched = toolNames.filter(n => n.toLowerCase().includes(value));

    matched.forEach(name => {
        const li = document.createElement("li");
        li.textContent = name;
        li.onclick = () => {
            input.value = name;
            document.querySelector(".search-form").submit();
        };
        box.appendChild(li);
    });
});
function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebar-overlay");

    sidebar.classList.toggle("open");

    if (sidebar.classList.contains("open")) {
        overlay.style.display = "block";
    } else {
        overlay.style.display = "none";
    }
}
