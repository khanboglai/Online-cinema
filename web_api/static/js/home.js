const searchBar = document.querySelector('.search-bar');
const searchSuggestions = document.querySelector('.search-suggestions');

searchBar.addEventListener('focus', () => {
    searchSuggestions.classList.add('active');
});

searchBar.addEventListener('blur', (e) => {
    setTimeout(() => {
        searchSuggestions.classList.remove('active');
    }, 200);
});

 
 // Add hover effect to video cards
 document.querySelectorAll('.video-card').forEach(card => {
    card.addEventListener('mouseover', () => {
        card.style.cursor = 'pointer';
    });
});

// Add search functionality
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        const query = document.querySelector('.search-bar').value;
        if (query) {
            window.location.href = '/search/' + encodeURIComponent(query) + '/page=1';
        }
    }
}

// Handle input changes for suggestions
function handleInput(event) {
    const query = event.target.value;
    const suggestionsBox = document.getElementById('suggestions');

    if (query.length > 0) {
        fetch(`/search/suggestions/${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                // Clear previous suggestions
                suggestionsBox.innerHTML = '';
                suggestionsBox.style.display = 'block';

                // Populate suggestions
                data.suggestions.forEach(suggestion => {
                    const suggestionItem = document.createElement('div');
                    suggestionItem.textContent = suggestion.title;
                    suggestionItem.classList.add('suggestion-item');
                    suggestionItem.onclick = () => {
                        window.location.href = `/films/${suggestion.id}`;
                    };
                    suggestionsBox.appendChild(suggestionItem);
                });
            })
            .catch(error => {
                console.error('Error fetching suggestions:', error);
            });
    } else {
        suggestionsBox.style.display = 'none';
    }
}

// Hide suggestions when clicking outside
document.addEventListener('click', (event) => {
    const suggestionsBox = document.getElementById('suggestions');
    if (!suggestionsBox.contains(event.target) && event.target !== document.querySelector('.search-bar')) {
        suggestionsBox.style.display = 'none';
    }
});

function editFilm(event, filmId) {
    event.stopPropagation(); // Останавливает всплытие события
    window.location.href = `/films/edit/${filmId}`; // Перенаправляет на страницу редактирования
}