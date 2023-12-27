function showWordDetails(word, translation, book, date, difficulty) {
    // Display word details in the modal
    document.getElementById('wordDetails').innerHTML = `
        <strong>Word:</strong> ${word}<br>
        <strong>Translation:</strong> ${translation}<br>
        <strong>Book:</strong> ${book}<br>
        <strong>Date:</strong> ${date}<br>
        <strong>Difficulty:</strong> ${difficulty}
    `;

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
    // Implement logic to remove the word (delete the record from the database)
    // You can use AJAX to send a request to the server
    // After removing the word, you may want to refresh the page or update the table dynamically

    // Get the word ID or any identifier needed for deletion
    var wordId = /* Add code to get the word ID */;

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