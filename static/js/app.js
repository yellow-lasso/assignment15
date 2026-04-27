document.addEventListener("DOMContentLoaded", () => {
    console.log("app.js loaded");

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

    function getChartLabelsAndValues(counts, limit = 10) {
        const entries = Object.entries(counts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, limit);

        return {
            labels: entries.map((entry) => entry[0]),
            values: entries.map((entry) => entry[1])
        };
    }

    function createBarChart(canvasId, title, labels, values) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || typeof Chart === "undefined") return;

        new Chart(canvas, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: title,
                        data: values,
                        borderWidth: 1,
                        borderRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }

    function createDoughnutChart(canvasId, labels, values) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || typeof Chart === "undefined") return;

        new Chart(canvas, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Trades",
                        data: values
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
        });
    }

    function renderCharts() {
        const tickerData = getChartLabelsAndValues(buildCountMap(tradeCards, "ticker"));
        const typeData = getChartLabelsAndValues(buildCountMap(tradeCards, "transactionType"));

        createBarChart(
            "tickerChart",
            "Trades by Ticker",
            tickerData.labels,
            tickerData.values
        );

        createDoughnutChart(
            "typeChart",
            typeData.labels,
            typeData.values
        );
    }

    if (searchInput) searchInput.addEventListener("input", filterTrades);
    if (typeFilter) typeFilter.addEventListener("change", filterTrades);
    if (sortFilter) sortFilter.addEventListener("change", sortTrades);

    renderCharts();

        function getTopEntry(counts) {
        const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
        return entries.length > 0 ? entries[0] : ["N/A", 0];
    }

    function renderRepresentativeAnalytics() {
        const profileCards = Array.from(document.querySelectorAll(".profile-trade-card"));

        if (profileCards.length === 0) return;

        const tickerCounts = buildCountMap(profileCards, "ticker");
        const typeCounts = buildCountMap(profileCards, "transactionType");

        const [topTicker, topTickerCount] = getTopEntry(tickerCounts);
        const [topType, topTypeCount] = getTopEntry(typeCounts);

        const topTickerStat = document.getElementById("topTickerStat");
        const topTypeStat = document.getElementById("topTypeStat");
        const profileInsight = document.getElementById("profileInsight");

        if (topTickerStat) topTickerStat.textContent = topTicker;
        if (topTypeStat) topTypeStat.textContent = topType;

        const tickerData = getChartLabelsAndValues(tickerCounts);
        const typeData = getChartLabelsAndValues(typeCounts);

        createBarChart(
            "profileTickerChart",
            "Trades by Ticker",
            tickerData.labels,
            tickerData.values
        );

        createDoughnutChart(
            "profileTypeChart",
            typeData.labels,
            typeData.values
        );

        if (profileInsight) {
            profileInsight.textContent =
                `This representative has ${profileCards.length} saved trade records. ` +
                `The most frequently appearing ticker is ${topTicker}, with ${topTickerCount} record(s). ` +
                `The most common transaction type is ${topType}, appearing ${topTypeCount} time(s).`;
        }
    }

    renderRepresentativeAnalytics();
});