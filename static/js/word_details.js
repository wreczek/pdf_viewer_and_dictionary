function showWordDetails(word, translation, book, date, difficulty, wordId) {
    // Display word details in the modal
    document.getElementById('wordDetails').innerHTML = `
        <strong>Word:</strong> ${word}<br>
        <strong>Translation:</strong> ${translation}<br>
        <strong>Book:</strong> ${book}<br>
        <strong>Date:</strong> ${date}<br>
        <strong>Difficulty:</strong> ${difficulty}
    `;

    // Set the wordId as a data attribute on the modal
    document.getElementById('wordDetailsModal').setAttribute('data-word-id', wordId);

    // Show the modal using Bootstrap's method
    $('#wordDetailsModal').modal('show');
}


function acceptChanges() {
    // Implement logic to accept changes (update the record in the database)
    // You can use AJAX to send a request to the server
    // After accepting changes, you may want to refresh the page or update the table dynamically
    // ...

    // Close the modal using Bootstrap's method
    $('#wordDetailsModal').modal('hide');
}


function removeWord() {
    // Get the word ID from the modal (data attribute)
    let wordId = document.getElementById('wordDetailsModal').getAttribute('data-word-id');
    // Assuming you have a way to get the CSRF token:
    let csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Log the wordId to the console for debugging
    console.log('Word ID:', wordId);

    // Check if wordId is available
    if (!wordId) {
        console.error('Word ID not found.');
        return;
    }

    // Flask route for deleting words
    let deleteUrl = `/delete_word/${wordId}`;

    // Use the Fetch API for AJAX, including CSRF token in the request headers
    fetch(deleteUrl, {
        method: 'DELETE',
        headers: {
            'X-CSRF-Token': csrfToken, // Ensure this header name matches what your server expects
            'Content-Type': 'application/json'
        },
        // You might need to include credentials if cookies are used for session management
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Word removed successfully:', data);
        $('#wordDetailsModal').modal('hide');
        fetchAndRefreshContent();
    })
    .catch(error => {
        console.error('Error removing word:', error);
    });
}
