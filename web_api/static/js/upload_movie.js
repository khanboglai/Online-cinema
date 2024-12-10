function handleSubmit(event) {
  event.preventDefault();

  const movieName = document.getElementById('movieName').value;
  const director = document.getElementById('director').value;
  const year = document.getElementById('year').value;
  const country = document.getElementById('country').value;

  const selectedRating = document.querySelector('.rating-option.selected');
  const rating = selectedRating ? selectedRating.dataset.rating : null;

  if (!rating) {
    alert('Please select an age rating');
    return;
  }

  if (!movieName || !director || !year || !country) {
    alert('Please fill in all required fields');
    return;
  }

  const movieData = {
    movieName,
    rating,
    director,
    year,
    country
  };

  console.log('Submitting movie data:', movieData);
  alert('Movie uploaded successfully!');

  window.location.href = "https://example.com/movies";
}

function goBack() {
  window.location.href = "/home";
}

document.addEventListener('DOMContentLoaded', () => {
  const ratingOptions = document.querySelectorAll('.rating-option');

  ratingOptions.forEach(option => {
    option.addEventListener('click', () => {
      ratingOptions.forEach(opt => opt.classList.remove('selected'));
      option.classList.add('selected');

      // Add ripple effect on click
      const ripple = document.createElement('div');
      ripple.classList.add('ripple');
      option.appendChild(ripple);

      setTimeout(() => {
        ripple.remove();
      }, 1000);
    });
  });

  const form = document.getElementById('movieUploadForm');
  const yearInput = document.getElementById('year');

  yearInput.addEventListener('input', () => {
    const currentYear = new Date().getFullYear();
    if (yearInput.value > currentYear) {
      yearInput.value = currentYear;
    }
  });

  const inputs = document.querySelectorAll('input');
  inputs.forEach(input => {
    input.addEventListener('focus', () => {
      input.style.borderColor = 'var(--secondary)';
    });

    input.addEventListener('blur', () => {
      if (!input.value) {
        input.style.borderColor = '#ddd';
      }
    });
  });
});
