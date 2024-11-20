function editProfile() {
  window.location.replace('/lk/edit');
}

document.addEventListener('DOMContentLoaded', () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.width = '75%';
      }
    });
  });

  const progressBar = document.querySelector('.progress');
  observer.observe(progressBar);

  const activityItems = document.querySelectorAll('.activity-item');
  activityItems.forEach(item => {
    item.addEventListener('mouseenter', () => {
      item.style.backgroundColor = '#f7f9fc';
    });
    item.addEventListener('mouseleave', () => {
      item.style.backgroundColor = 'white';
    });
  });

  const movieCards = document.querySelectorAll('.movie-card');
  movieCards.forEach(card => {
    card.addEventListener('click', () => {
      alert('Movie details coming soon!');
    });
  });
});
