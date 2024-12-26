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

// Handle input changes for suggestions
async function handleInput(event) {
    const query = event.target.value;
    const suggestionsBox = document.getElementById('suggestions');

    if (query.length > 0) {
        try {
            const response = await fetch(`/manage/suggest/${encodeURIComponent(query)}`);
            const data = await response.json();

            // Clear previous suggestions
            suggestionsBox.innerHTML = '';
            suggestionsBox.style.display = 'block';

            // Populate suggestions
            data.suggestions.forEach(suggestion => {
                const suggestionItem = document.createElement('div');
                suggestionItem.textContent = suggestion.login;
                suggestionItem.classList.add('suggestion-item');
                suggestionItem.onclick = () => handleSuggestionClick(suggestion);
                suggestionsBox.appendChild(suggestionItem);
            });
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    } else {
        suggestionsBox.style.display = 'none';
    }
}

async function handleSuggestionClick(suggestion) {
    const confirmation = confirm(`Вы уверены, что хотите удалить пользователя ${suggestion.login}?`);
    if (!confirmation) {
        return;
    }
    try {
        const deleteResponse = await fetch(`/manage/delete/${suggestion.id}`, {
            method: 'POST',
        });
        if (deleteResponse.ok) {
            // Успешно удалено, можно обновить интерфейс или сделать что-то еще
            console.log(`Пользователь ${suggestion.login} удален.`);
        } else {
            console.error('Ошибка при удалении пользователя:', deleteResponse.statusText);
        }
    } catch (error) {
        console.error('Ошибка при отправке запроса на удаление:', error);
    }
}

// Hide suggestions when clicking outside
document.addEventListener('click', (event) => {
    const suggestionsBox = document.getElementById('suggestions');
    if (!suggestionsBox.contains(event.target) && event.target !== document.querySelector('.search-bar')) {
        suggestionsBox.style.display = 'none';
    }
});
