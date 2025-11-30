//dodany kod z guzikami w osobnym pliku zeby nie bylo spaghetti
document.addEventListener("DOMContentLoaded", () =>{
    const navItems = document.querySelectorAll(".nav-item");
    navItems.forEach((btn) => {
        btn.addEventListener("click",() =>{
            const target = btn.dataset.target;
            if (target) {
                window.location.href = target;
            }
        });
    });
});