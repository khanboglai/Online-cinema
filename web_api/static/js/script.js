function editProfile() {
  window.location.replace('/lk/edit');
}

function goLK() {
  window.location.replace('/lk/');
}

function logout() {
  window.location.replace('/logout')
}

async function handleLogin(event) {
  event.preventDefault(); // Предотвращаем стандартное поведение формы

  const formData = new FormData(document.getElementById('profileForm'));
  const response = await fetch('/lk/edit', {
      method: 'POST',
      body: formData
  });
  if (!response.ok) {
      const result = await response.json();
      document.getElementById('errorMessage').textContent = result.error;
      document.getElementById('errorMessage').style.display = 'block';
  } else {
      window.location.replace("/lk/");
  }
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

function handleSubmit(event) {
  event.preventDefault();
  let isValid = true;
  const errors = document.querySelectorAll('.error-message');
  errors.forEach(error => error.style.display = 'none');

  const name = document.getElementById('name').value;
  if (name.length < 2) {
    document.getElementById('nameError').style.display = 'block';
    isValid = false;
  }

  // const currentPassword = document.getElementById('currentPassword').value;
  // const newPassword = document.getElementById('newPassword').value;
  // const confirmPassword = document.getElementById('confirmPassword').value;

  // if (currentPassword.length === 0) {
  //   document.getElementById('currentPasswordError').style.display = 'block';
  //   isValid = false;
  // }

  // if (newPassword) {
  //   if (newPassword.length < 8) {
  //     document.getElementById('newPasswordError').style.display = 'block';
  //     isValid = false;
  //   }
  //   if (newPassword !== confirmPassword) {
  //     document.getElementById('confirmPasswordError').style.display = 'block';
  //     isValid = false;
  //   }
  // }

  const birthDate = new Date(document.getElementById('birthDate').value);
  const today = new Date();
  if (birthDate > today) {
    document.getElementById('birthDateError').style.display = 'block';
    isValid = false;
  }

  if (isValid) {
    alert('Profile updated successfully!');
    goBack();
  }

  return false;
}

function goBack() {
  window.location.href = '/lk';
}

async function changeSubscription(userId, setTo) {
  const formData = new FormData();
  formData.append('user_id', userId);
  formData.append('set_to', setTo);
  const response = fetch(
      `http://localhost:8000/lk/subscription`, {
        method: 'POST',
        body: formData
      }
  ).then(response => {
    if (!response.ok) throw Error("Subscription update error");
    console.log("Subscription plan was updated successfully");

    location.reload()
  }).catch(error => console.error(error));
}

// document.addEventListener('DOMContentLoaded', () => {
//   document.getElementById('birthDate').value = '1990-01-01';

//   const inputs = document.querySelectorAll('input');
//   inputs.forEach(input => {
//     input.addEventListener('input', function() {
//       if (this.value) {
//         this.style.borderColor = '#4CAF50';
//       } else {
//         this.style.borderColor = '#ddd';
//       }
//     });
//   });
// });
