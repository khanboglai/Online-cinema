async function handleSubmit(event) {
    event.preventDefault();

    const movieName = document.getElementById('filmName').value;
    // const director = document.getElementById('director').value;
    const year = document.getElementById('year').value;
    const country = document.getElementById('country').value;
    const movieFile = document.getElementById('filmFile').files[0];

    const selectedRating = document.querySelector('input[name="age_rating"]:checked');
    const rating = selectedRating ? selectedRating.value : null;

    if (!rating) {
        alert('Please select an age rating');
        return;
    }

    if (!movieName || !year || !country || !movieFile) {
        alert('Please fill in all required fields');
        return;
    }

    // Создание FormData для отправки данных
    const formData = new FormData();
    formData.append('film_name', movieName);
    formData.append('age_rating', rating);
    // formData.append('director', director);
    formData.append('year', year);
    formData.append('country', country);
    formData.append('film_file', movieFile);

    console.log(formData);

    try {
        const response = await fetch('http://localhost:8000/upload', {
            method: 'POST',
            body: formData,
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

  const fileInput = document.getElementById('filmFile');
  const fileName = document.querySelector('.file-name');
  
  fileInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
      fileName.textContent = this.files[0].name;
    } else {
      fileName.textContent = 'Choose a file...';
    }
  });
});
