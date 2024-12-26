async function handleSubmit(event) {
  event.preventDefault();

  const movieName = document.getElementById('filmName').value;
  const year = document.getElementById('year').value;
  const country = document.getElementById('country').value;
  const description = document.getElementById('description').value;
  const actor = document.getElementById('actor').value;
  const genre = document.getElementById('genre').value;
  const studios = document.getElementById('studios').value;
  const tags = document.getElementById('tags').value;
  const director = document.getElementById('director').value;

  const selectedRating = document.querySelector('input[name="age_rating"]:checked');

  const rating = selectedRating ? selectedRating.value : null;

  if (!rating) {
      alert('Please select an age rating');
      return;
  }

  if (!movieName || !year || !country || !description || !actor || !genre || !studios || !tags || !director) {
      alert('Please fill in all required fields');
      return;
  }

  // Показать индикатор загрузки
  const loadingIndicator = document.getElementById('loadingIndicator');
  loadingIndicator.style.display = 'flex';

  // Создание FormData для отправки данных
  const formData = new FormData();
  formData.append('film_name', movieName);
  formData.append('age_rating', rating);
  formData.append('director', director);
  formData.append('year', year);
  formData.append('country', country);
  formData.append('description', description);
  formData.append('actor', actor);
  formData.append('genre', genre);
  formData.append('studios', studios);
  formData.append('tags', tags);
  formData.append('id', filmId)

  try {
      const response = await fetch('http://localhost:8000/films/edit', {
          method: 'POST',
          body: formData
      });

      if (!response.ok) {
          const errorResponse = await response.json();
          console.error('Server Error:', errorResponse);
          alert('Failed to upload the film. Please try again.');
          return;
      }

      const result = response.ok;
      console.log('Upload successful:', result);
      window.location.href = "http://localhost:8000/home";
  } catch (error) {
      console.error('Network Error:', error);
      alert('An error occurred. Please check your internet connection and try again.');
  } finally {
      // Скрыть индикатор загрузки
      loadingIndicator.style.display = 'none';
  }
}


function goBack() {
  window.location.href = "/home";
}

document.addEventListener('DOMContentLoaded', () => {
  const yearInput = document.getElementById('year');

  yearInput.addEventListener('input', () => {
    const currentYear = new Date().getFullYear();
    if (yearInput.value > currentYear) {
      yearInput.value = currentYear;
    }
  });

  const inputs = document.querySelectorAll('input[type="text"], input[type="number"]');
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