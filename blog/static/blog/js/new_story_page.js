document.addEventListener('DOMContentLoaded', () => {
    const publishButton = document.getElementById('publish-button')
    const titleInput = document.getElementById('title-input')
    const storyTextArea = document.getElementById('story-textarea')

    function togglePublishButton() {
        publishButton.disabled = titleInput.value.trim() === '' || storyTextArea.value.trim() === ''
    }

    togglePublishButton()

    titleInput.addEventListener('input', togglePublishButton)
    storyTextArea.addEventListener('input', togglePublishButton)
})

document.getElementById('publish-button').addEventListener('click', () => {
    const submitButton = document.getElementById('submit-button')
    submitButton.click()
})

document.getElementById('image').addEventListener('change', (event) => {
    const file = event.target.files[0]

    if (file) {
        const reader = new FileReader()
        const previewImage = document.getElementById('preview')

        reader.onload = (e) => {
            const imageBanner = document.getElementById('image-banner')
            const bannerAlreadyExists = document.getElementById('image-banner-already-exists')

            if (imageBanner !== null) {
                imageBanner.style.display = 'none'
            }
            if (bannerAlreadyExists !== null) {
                bannerAlreadyExists.style.display = 'none'
            }

            previewImage.style.backgroundImage = `url(${e.target.result})`
            previewImage.style.backgroundSize = 'cover'
            previewImage.style.backgroundPosition = 'center'
        }
        reader.readAsDataURL(file)
    }
})
