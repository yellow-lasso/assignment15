document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("tradeSearch");
    const typeFilter = document.getElementById("typeFilter");
    const sortFilter = document.getElementById("sortFilter");
    const tradeList = document.getElementById("tradeList");
    const tradeCards = Array.from(document.querySelectorAll(".trade-card"));
    const emptyMessage = document.getElementById("filterEmptyMessage");

    const deleteLinks = document.querySelectorAll(".delete-link");

    deleteLinks.forEach((link) => {
        link.addEventListener("click", (event) => {
            const confirmed = confirm("Are you sure you want to delete this trade? This action cannot be undone.");
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });

    function filterTrades() {
        if (!searchInput || !typeFilter || !emptyMessage) return;

        const searchTerm = searchInput.value.toLowerCase();
        const selectedType = typeFilter.value.toLowerCase();
        let visibleCount = 0;

        tradeCards.forEach((card) => {
            const text = card.innerText.toLowerCase();
            const tradeType = card.dataset.transactionType.toLowerCase();

            const matchesSearch = text.includes(searchTerm);
            const matchesType = selectedType === "all" || tradeType === selectedType;

            if (matchesSearch && matchesType) {
                card.style.display = "block";
                visibleCount++;
            } else {
                card.style.display = "none";
            }
        });

        emptyMessage.style.display = visibleCount === 0 ? "block" : "none";
    }

    function sortTrades() {
        if (!sortFilter || !tradeList) return;

        const sortValue = sortFilter.value;

        const sortedCards = [...tradeCards].sort((a, b) => {
            if (sortValue === "newest") {
                return b.dataset.tradeDate.localeCompare(a.dataset.tradeDate);
            }

            if (sortValue === "oldest") {
                return a.dataset.tradeDate.localeCompare(b.dataset.tradeDate);
            }

            if (sortValue === "ticker") {
                return a.dataset.ticker.localeCompare(b.dataset.ticker);
            }

            if (sortValue === "representative") {
                return a.dataset.representative.localeCompare(b.dataset.representative);
            }

            if (sortValue === "type") {
                return a.dataset.transactionType.localeCompare(b.dataset.transactionType);
            }

            return 0;
        });

        sortedCards.forEach((card) => tradeList.appendChild(card));
        filterTrades();
    }

    function buildCountMap(cards, key) {
        const counts = {};

        cards.forEach((card) => {
            const value = card.dataset[key] || "Unknown";
            counts[value] = (counts[value] || 0) + 1;
        });

        return counts;
    }

    function renderBarChart(containerId, counts) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = "";

        const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);

        if (entries.length === 0) {
            container.innerHTML = "<p>No data available.</p>";
            return;
        }

        const maxValue = Math.max(...entries.map((entry) => entry[1]));

        entries.forEach(([label, value]) => {
            const row = document.createElement("div");
            row.className = "bar-row";

            const labelEl = document.createElement("div");
            labelEl.className = "bar-label";
            labelEl.textContent = label;

            const barWrap = document.createElement("div");
            barWrap.className = "bar-wrap";

            const bar = document.createElement("div");
            bar.className = "bar-fill";
            bar.style.width = `${(value / maxValue) * 100}%`;
            bar.textContent = value;

            barWrap.appendChild(bar);
            row.appendChild(labelEl);
            row.appendChild(barWrap);

            container.appendChild(row);
        });
    }

    function renderCharts() {
        renderBarChart("tickerChart", buildCountMap(tradeCards, "ticker"));
        renderBarChart("typeChart", buildCountMap(tradeCards, "transactionType"));
    }

    if (searchInput) searchInput.addEventListener("input", filterTrades);
    if (typeFilter) typeFilter.addEventListener("change", filterTrades);
    if (sortFilter) sortFilter.addEventListener("change", sortTrades);

    renderCharts();
});