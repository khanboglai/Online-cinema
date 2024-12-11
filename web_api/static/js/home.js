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