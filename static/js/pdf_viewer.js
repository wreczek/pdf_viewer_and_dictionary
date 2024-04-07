// Function to set the last position for the PDF viewer
function setLastPosition(lastPosition, currentFile) {
    // Set the last position if available
    if (lastPosition) {
        document.getElementById('pdfViewer').contentWindow.scrollTo(0, lastPosition);
    }

    // Save the scroll position on window unload
    window.addEventListener('beforeunload', function () {
        let scrollPosition = document.getElementById('pdfViewer').contentWindow.scrollY;
        document.cookie = `last_position_${currentFile}=${scrollPosition}`;
    });
}
