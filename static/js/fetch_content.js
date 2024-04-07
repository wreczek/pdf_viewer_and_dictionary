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
    }
    catch (error) {
        console.error('Error fetching data:', error);
    }
}
