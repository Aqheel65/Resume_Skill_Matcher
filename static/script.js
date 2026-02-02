const btn = document.querySelector(".btn");

if (btn) {
    btn.addEventListener("click", () => {
        btn.innerText = "Analyzing...";
        btn.style.opacity = "0.8";
    });
}
document.addEventListener("DOMContentLoaded", () => {
    const bar = document.getElementById("progressBar");
    const text = document.getElementById("progressText");

    if (!bar) return;

    const score = parseInt(bar.dataset.score);
    let current = 0;

    // Color logic
    if (score < 40) bar.classList.add("progress-low");
    else if (score < 70) bar.classList.add("progress-mid");
    else bar.classList.add("progress-high");

    // Animation
    const interval = setInterval(() => {
        if (current >= score) {
            clearInterval(interval);
        } else {
            current++;
            bar.style.width = current + "%";
            text.textContent = current + "%";
        }
    }, 20);
});
