document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.getElementById('username')
    const passwordInput = document.getElementById('password')
    const loginButton = document.getElementById('login-button')

    function toggleLoginButton() {
        loginButton.disabled = usernameInput.value.trim() === '' || passwordInput.value.trim() === ''
    }

    toggleLoginButton()

    usernameInput.addEventListener('input', toggleLoginButton)
    passwordInput.addEventListener('input', toggleLoginButton)
})
