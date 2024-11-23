 // Add hover effect to video cards
 document.querySelectorAll('.video-card').forEach(card => {
    card.addEventListener('mouseover', () => {
        card.style.cursor = 'pointer';
    });
});

// Add search functionality
const searchBar = document.querySelector('.search-bar');
searchBar.addEventListener('keyup', (e) => {
    if(e.key === 'Enter') {
        console.log('Searching for:', searchBar.value);
    }
});

// Add logout confirmation
document.getElementById('logoutForm').addEventListener('submit', function(e) {
    if(!confirm('Are you sure you want to logout?')) {
        e.preventDefault();
    }
});