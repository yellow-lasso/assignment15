document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("tradeSearch");
    const typeFilter = document.getElementById("typeFilter");
    const tradeCards = document.querySelectorAll(".trade-card");
    const emptyMessage = document.getElementById("filterEmptyMessage");

    function filterTrades() {
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

    searchInput.addEventListener("input", filterTrades);
    typeFilter.addEventListener("change", filterTrades);
});