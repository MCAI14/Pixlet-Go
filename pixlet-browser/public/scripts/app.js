document.addEventListener('DOMContentLoaded', () => {
    const greetingElement = document.createElement('h1');
    greetingElement.textContent = 'Welcome to Pixlet!';
    document.body.appendChild(greetingElement);

    const buttonElement = document.createElement('button');
    buttonElement.textContent = 'Open Pixlet Home';
    document.body.appendChild(buttonElement);

    // Open Pixlet site in a new tab when the button is clicked
    buttonElement.addEventListener('click', () => {
        window.open('https://pixlet.netlify.app', '_blank');
    });

    const searchForm = document.createElement("form");
    const searchInput = document.createElement("input");
    const searchButton = document.createElement("button");

    searchInput.type = "text";
    searchInput.placeholder = "Search the web...";
    searchButton.textContent = "Go";

    searchForm.appendChild(searchInput);
    searchForm.appendChild(searchButton);
    document.body.insertBefore(searchForm, document.querySelector("main"));

    searchForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
            try {
                window.open(`https://www.google.com/search?q=${encodeURIComponent(query)}`, "_blank");
            } catch (error) {
                console.error("Failed to open the search URL:", error);
            }
        } else {
            alert("Please enter a search query.");
        }
    });
});