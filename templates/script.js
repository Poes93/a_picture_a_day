document.getElementById('upload-form').addEventListener('submit', function(event) {
    event.preventDefault();

    let imageInput = document.getElementById('image-input');
    if (imageInput.files.length === 0) {
        alert('Please select an image to upload.');
        return;
    }

    // TODO: Add AJAX request to upload the image to the server
    console.log('Image submitted for upload:', imageInput.files[0]);

    // Reset the form after upload
    imageInput.value = '';
});
