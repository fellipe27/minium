document.addEventListener('DOMContentLoaded', () => {
    const emailInput = document.getElementById('email')
    const usernameInput = document.getElementById('username')
    const passwordInput = document.getElementById('password')
    const monthInput = document.getElementById('month')
    const dayInput = document.getElementById('day')
    const yearInput = document.getElementById('year')
    const registerButton = document.getElementById('register-button')

    function toggleRegisterButton() {
        registerButton.disabled = emailInput.value.trim() === '' ||
            usernameInput.value.trim() === '' ||
            passwordInput.value.trim() === ''
    }

    function validateInput(event) {
        if (event.key === '-') {
            event.preventDefault()
        }
    }

    function validateMonth() {
        const month = monthInput.value

        const numMonth = parseInt(month, 10)

        if (numMonth < 1 || numMonth > 12 || isNaN(numMonth)) {
            monthInput.value = ''
        }

        validateDay()
    }

    function validateDay() {
        const month = parseInt(monthInput.value, 10)
        const day = dayInput.value
        const year = parseInt(yearInput.value, 10) || new Date().getFullYear()

        const numDay = parseInt(day, 10)
        const daysInMonth = new Date(year, month, 0).getDate()

        if (numDay < 1 || numDay > daysInMonth || numDay > 31 || isNaN(numDay) || day.length > 2) {
            dayInput.value = ''
        }
    }

    function validateYear() {
        const year = yearInput.value
        const currentYear = new Date().getFullYear()

        if (year.length === 4) {
            const numYear = parseInt(year, 10)

            if (numYear < 1900 || numYear > currentYear || isNaN(numYear)) {
                yearInput.value = ''
            }
        } else if (year.length > 4) {
            yearInput.value = ''
        }
    }

    toggleRegisterButton()

    emailInput.addEventListener('input', toggleRegisterButton)
    usernameInput.addEventListener('input', toggleRegisterButton)
    passwordInput.addEventListener('input', toggleRegisterButton)

    [monthInput, dayInput, yearInput].forEach((input) => {
        input.addEventListener('keydown', validateInput)
        input.addEventListener('input', () => {
            if (input === monthInput) {
                validateMonth()
            }
            if (input === dayInput) {
                validateDay()
            }
            if (input === yearInput) {
                validateYear()
            }
        })
    })
})
