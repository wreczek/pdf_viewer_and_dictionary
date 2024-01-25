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

        // Ensure the server response is valid JSON
        return response.json();
    })
    .then(data => {
    // Ensure data is defined before logging
    console.log('Word removed successfully:', data);

    // Close the modal using Bootstrap's method
    $('#wordDetailsModal').modal('hide');

    // Fetch and refresh content after removal
    fetchAndRefreshContent();
    })
    .catch(error => {
        // Handle errors (e.g., show an error message)
        console.error('Error removing word:', error);
    });
}

// Assuming this function is called to fetch and update content
async function fetchAndRefreshContent() {
    // Log message before the fetch request
    console.log('Fetching and refreshing content...');

  try {
    const response = await fetch('/get_updated_content');
    const data = await response.json();

    console.log('Content fetched and refreshed successfully:', data);

    // Assuming 'content-container' is the container where you want to update the HTML
    document.getElementById('refreshedContent').innerHTML = data.html;
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}

// Set an interval to fetch and refresh content every 5 seconds (adjust as needed)
//setInterval(fetchAndRefreshContent, 10000);

// Function to set the last position for the PDF viewer
function setLastPosition(lastPosition, currentFile) {
    // Set the last position if available
    if (lastPosition) {
        document.getElementById('pdfViewer').contentWindow.scrollTo(0, lastPosition);
    }

    // Save the scroll position on window unload
    window.addEventListener('beforeunload', function () {
        var scrollPosition = document.getElementById('pdfViewer').contentWindow.scrollY;
        document.cookie = `last_position_${currentFile}=${scrollPosition}`;
    });
}

// Use the function to set the last position when the page loads
setLastPosition("{{ last_position }}", "{{ current_file }}");

$(document).ready(function () {
    $('#filterForm').submit(function (event) {
        event.preventDefault();  // Prevent the default form submission

        // Serialize form data
        var formData = $(this).serialize();

        // Send an AJAX request
        $.ajax({
            type: 'POST',
            url: "{{ url_for('unfamiliar_words_partial') }}",
            data: formData,
            success: function (data) {
                // Update the table content with the response
                $('#refreshedContent').html(data);

                // After updating the content, fetch and refresh additional content
                fetchAndRefreshContent();
            },
            error: function () {
                console.error('Error occurred during AJAX request');
            }
        });
    });
});
