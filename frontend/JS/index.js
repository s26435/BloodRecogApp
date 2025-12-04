//ten plik odpowiada za obsługuę funkcjonalności zakładki home stworzonej w index.html


document.addEventListener("DOMContentLoaded", () => {
    const totalEl = document.getElementById("total-analyses");
    const lastAgoEl = document.getElementById("last-analysis-ago");
    const recentListEl = document.getElementById("recent-analysis");
    const chartContainer = document.getElementById("chart-placeholder");
    let analyses = [];

    async function fetchAnalyses() {
        try {
            const res = await fetch("/api/analyses/");
            if (!res.ok) throw new Error("Nie udało się pobrać analiz z bazy :(");
            analyses = await res.json();
        } catch (err) {
            console.error(err);
            analyses = [];
        }
    }

    function parseCreatedAt(str) {
        if (!str) return null;
        const normalized = str.replace(" ","T");
        const d = new Date(normalized);
        return isNaN(d.getTime()) ? null : d;
    }

    function timeAgo(date) {
        if (!date) return "-";
        const now = new Date();
        let diffMs = now - date;
        if (diffMs < 0) diffMs = 0;

        const minutes = Math.floor(diffMs / (1000*60));
        const hours = Math.floor(diffMs / (1000*60*60));
        const days = Math.floor(diffMs / (1000 * 60 *60*24));

        if (minutes < 60) {
            return `${minutes} min`
        } else if (hours < 24) {
            return `${hours} h`
        } else {
            return `${days} dni`
        }
    }
    function getLocalDateKey(d){
        const y =d.getFullYear();
        const m = String(d.getMonth()+1).padStart(2,"0");
        const day= String(d.getDate()).padStart(2,"0");
        return `${y}-${m}-${day}`
    }

    function buildDailyCounts() {
        const today = new Date();
        today.setHours(0, 0, 0, 0); 
        const days = [];

        for (let daysAgo = 30; daysAgo >= 0; daysAgo--) {
            const d = new Date(today);
            d.setDate(today.getDate() - daysAgo);
            days.push({
                key: getLocalDateKey(d),
                label: 30 - daysAgo, 
                count: 0,
            });
        }
        analyses.forEach((a) => {
            const d = parseCreatedAt(a.created_at);
            if (!d) return;
            d.setHours(0, 0, 0, 0);
            const key = getLocalDateKey(d);
            const dayObj = days.find((dd) => dd.key === key);
            if (dayObj) dayObj.count += 1;
        });
        return days;
    }

    function renderChart(){
        if (!chartContainer) return;
        const days = buildDailyCounts();
        const maxCount = Math.max(
            1,
            ...days.map((d) => d.count)
        );
        chartContainer.innerHTML = "";
        const barsWrapper = document.createElement("div");
        barsWrapper.className = "chart-bars";

        days.forEach((d, index) => {
            const barWrapper = document.createElement("div");
            barWrapper.className = "chart-bar-wrapper";
            const bar = document.createElement("div");
            bar.className = "chart-bar";
            if (d.count === 0) {
                bar.classList.add("chart-bar--zero");
            }

            const heightPercent = (d.count / maxCount) * 100;
            bar.style.height = `${heightPercent || 2}%`
            if (index % 5 === 0 || index === days.length - 1) {
                const label = document.createElement("span");
                label.className = "chart-bar-label";
                label.textContent = d.label;
                barWrapper.appendChild(label);
            }
            bar.title = `${d.count} analiz`;
            barWrapper.appendChild(bar);
            barsWrapper.appendChild(barWrapper);
        });
        chartContainer.appendChild(barsWrapper);
    }
    function renderStats() {
        if (totalEl) {
            totalEl.textContent = analyses.length.toString();
        }
        if (lastAgoEl) {
            if (analyses.length === 0) {
                lastAgoEl.textContent = "-";
            } else {
                const sorted = analyses
                    .slice()
                    .sort(
                        (a, b) =>
                            new Date(b.created_at || 0) -
                            new Date(a.created_at || 0)
                    );
                const last = sorted[0];
                const d = parseCreatedAt(last.created_at);
                lastAgoEl.textContent = timeAgo(d);
            }
        }
    }

    function renderRecent() {
        if (!recentListEl) return;
        recentListEl.innerHTML = "";

        if (analyses.length === 0) {
            const li = document.createElement("li");
            li.className = "recent-item recent-item--empty";
            li.textContent = "Brak zapisanych analiz";
            recentListEl.appendChild(li);
            return;
        }

        const sorted = analyses
            .slice()
            .sort(
                (a, b) =>
                    new Date(b.created_at || 0) -
                    new Date(a.created_at || 0)
            )
            .slice(0, 3);

        sorted.forEach((a, idx) => {
            const li = document.createElement("li");
            li.className = "recent-item";
            li.dataset.analysisId = a.id;

            const dot = document.createElement("div");
            dot.className =
                "recent-dot " + (idx === 0 ? "recent-dot--hot" : "");

            const main = document.createElement("div");
            main.className = "recent-main";

            const title = document.createElement("span");
            title.className = "recent-title";
            title.textContent = a.name || a.id;

            const date = parseCreatedAt(a.created_at);
            const meta = document.createElement("span");
            meta.className = "recent-meta";
            meta.textContent = date
                ? `Utworzono ${timeAgo(date)} temu`
                : (a.created_at || "");

            main.appendChild(title);
            main.appendChild(meta);

            li.appendChild(dot);
            li.appendChild(main);

            li.addEventListener("click", () => {
                window.location.href = `/history?analysis_id=${encodeURIComponent(
                    a.id
                )}`;
            });

            recentListEl.appendChild(li);
        });
    }

    (async () => {
        await fetchAnalyses();
        renderStats();
        renderChart();
        renderRecent();
    })();
});







