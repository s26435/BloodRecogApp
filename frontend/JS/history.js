//ten plik odpowiada za pobieranie z bazy analiz i oddawanie ich 
//zeby w historii sie pokazywalo

document.addEventListener("DOMContentLoaded", () => {
    const table = document.querySelector(".history-table");
    const searchInput = document.querySelector(".history-search");
    const detailCard = document.querySelector(".card--analysis-detail");

    if (!table) return;
    let analyses = [];
    async function fetchAnalyses() {
        try {
            const res = await fetch("/api/analyses/");
            if (!res.ok) throw new Error("NIe pobrała się historia");
            analyses = await res.json();
        } catch (error) {
            console.error(error);
        }
    }

    function renderList(filterText=""){ //tworzenie listy
        const existingRows = table.querySelectorAll(".history-row");
        existingRows.forEach((row) => row.remove());
        const norm = filterText.trim().toLowerCase();
        const filtered = analyses
            .slice()
            .sort(
                (a, b) =>
                    new Date(b.created_at || 0) - new Date(a.created_at || 0)
            )
            .filter((a) => {
                if (!norm) return true;
                const haystack = `${a.name} ${a.id}`.toLowerCase();
                return haystack.includes(norm);
            });
        
        filtered.forEach((a) => {
            const row = document.createElement("button");
            row.className = "history-row";
            row.innerHTML = `
                <span>${a.name || a.id}</span>
                <span>${a.created_at || ""}</span>
                <span class="status-pill--success">Zakończona</span>
                <span class="history-col--actions">Otwórz</span>
            `;
            row.addEventListener("click",() => showDetails(a));
            table.appendChild(row);
        });
    }

    function showDetails(a) {
        if (!detailCard) return;
        detailCard.style.display = "block";

        const titleEl = detailCard.querySelector(".analysis-title");
        const dateEl = detailCard.querySelector(".analysis-date");
        const notesEl = detailCard.querySelector(".analysis-notes");
        const imgOriginal = detailCard.querySelector(".analysis-img-original");
        const imgResult = detailCard.querySelector(".analysis-img-result");

        if (titleEl) titleEl.textContent = a.name || a.id;
        if (dateEl) dateEl.textContent = a.created_at || "";
        if (notesEl) notesEl.textContent = a.notes || "Brak notatek";
        if (imgOriginal) imgOriginal.src = a.original_image_url;
        if (imgResult) imgResult.src = a.processed_image_url;
    }

    (async () => {
        await fetchAnalyses();
        renderList();

        const params = new URLSearchParams(window.location.search);
        const selectedId = params.get("analysis_id");
        if (selectedId) {
            const selected = analyses.find((a) => a.id ===selectedId);
            if (selected) showDetails(selected);
        }
        if (searchInput){
            searchInput.addEventListener("input", () =>
            renderList(searchInput.value)
            );
        };
    })();
});






