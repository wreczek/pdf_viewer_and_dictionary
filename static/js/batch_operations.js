function performBatchOperation(operation) {
    const selectedFiles = getSelectedFileNames();
    if (selectedFiles.length === 0) {
        alert('Please select at least one file.');
        return;
    }

    const formData = new FormData();
    formData.append('filenames', JSON.stringify(selectedFiles));
    formData.append('operation', operation);

    // Include CSRF token if needed
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;
    formData.append('csrf_token', csrfToken);

    fetch('/perform_batch_operation', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reload the page to reflect the changes or reset checkboxes if not reloading
             window.location.reload();
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}
