document.addEventListener('DOMContentLoaded', () => {
    const updateButton = document.getElementById('update-button')
    const bioTextarea = document.getElementById('bio')

    function toggleUpdateButton() {
        updateButton.disabled = bioTextarea.value.trim() === ''
    }

    toggleUpdateButton()

    bioTextarea.addEventListener('input', toggleUpdateButton)
})

document.getElementById('image').addEventListener('change', (event) => {
    const file = event.target.files[0]

    if (file) {
        const reader = new FileReader()
        const previewImage = document.getElementById('preview')
        const userProfilePicture = document.getElementById('user-profile-picture')
        const previousPicture = document.getElementById('previous-picture')

        reader.onload = (e) => {
            if (userProfilePicture) {
                userProfilePicture.style.display = 'none'
            }
            if (previousPicture) {
                previousPicture.style.display = 'none'
            }

            previewImage.style.backgroundImage = `url(${e.target.result})`
            previewImage.style.backgroundSize = 'cover'
            previewImage.style.backgroundPosition = 'center'
        }
        reader.readAsDataURL(file)
    }
})
