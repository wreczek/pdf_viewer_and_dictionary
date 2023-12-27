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

    // Show the modal
    var wordDetailsModal = new bootstrap.Modal(document.getElementById('wordDetailsModal'));
    wordDetailsModal.show();
}

function acceptChanges() {
    // Implement logic to accept changes (update the record in the database)
    // You can use AJAX to send a request to the server
    // After accepting changes, you may want to refresh the page or update the table dynamically
    // ...

    // Close the modal
    var wordDetailsModal = new bootstrap.Modal(document.getElementById('wordDetailsModal'));
    wordDetailsModal.hide();
}

function removeWord() {
    // Get the word ID from the modal (data attribute)
    var wordId = document.getElementById('wordDetailsModal').getAttribute('data-word-id');

    // Log the wordId to the console for debugging
    console.log('Word ID:', wordId);

    // Check if wordId is available
    if (!wordId) {
        console.error('Word ID not found.');
        return;
    }

    // Assuming you have a Flask route for deleting words, modify the URL accordingly
    var deleteUrl = `/delete_word/${wordId}`;

    // Use the Fetch API for AJAX
    fetch(deleteUrl, {
        method: 'DELETE',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // Assuming the server returns some indication of success
        return response.json();
    })
    .then(data => {
        // Handle success (e.g., update UI, refresh page, etc.)
        console.log('Word removed successfully:', data);
        // Close the modal
        var wordDetailsModal = new bootstrap.Modal(document.getElementById('wordDetailsModal'));
        wordDetailsModal.hide();
        // Optionally, refresh the page or update the table
    })
    .catch(error => {
        // Handle errors (e.g., show an error message)
        console.error('Error removing word:', error);
    });
}
