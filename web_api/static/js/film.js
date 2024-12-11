const video = document.getElementById('videoPlayer');
const playPauseBtn = document.getElementById('playPauseBtn');
const fullscreenBtn = document.getElementById('fullscreenBtn');
const progressBar = document.getElementById('progressBar');
const progress = document.getElementById('progress');
const coverOverlay = document.getElementById('coverOverlay');
const filmCover = document.getElementById('filmCover');
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

// Cover overlay click handler
coverOverlay.addEventListener('click', () => {
    coverOverlay.classList.add('hidden');
    filmCover.style.display = 'none';
    video.style.display = 'block'; // Показываем видео
    video.play();
    playPauseBtn.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>';
});
// Play/Pause
playPauseBtn.addEventListener('click', () => {
    if (video.paused) {
        video.play();
        playPauseBtn.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>';
    } else {
        video.pause();
        playPauseBtn.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>';
    }
});

// Fullscreen
fullscreenBtn.addEventListener('click', () => {
    if (video.requestFullscreen) {
        video.requestFullscreen();
    } else if (video.webkitRequestFullscreen) {
        video.webkitRequestFullscreen();
    } else if (video.msRequestFullscreen) {
        video.msRequestFullscreen();
    }
});

// Progress bar
video.addEventListener('timeupdate', () => {
    const percentage = (video.currentTime / video.duration) * 100;
    progress.style.width = percentage + '%';
});

progressBar.addEventListener('click', (e) => {
    const rect = progressBar.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    video.currentTime = pos * video.duration;
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

