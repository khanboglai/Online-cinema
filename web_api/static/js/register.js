async function handleLogin(event) {
    event.preventDefault(); // Предотвращаем стандартное поведение формы

    const formData = new FormData(document.getElementById('loginForm'));
    const response = await fetch('/register', {
        method: 'POST',
        body: formData
    });
    if (!response.ok) {
        const result = await response.json();
        document.getElementById('errorMessage').textContent = result.error;
        document.getElementById('errorMessage').style.display = 'block';
    } else {
        window.location.reload();
    }
}