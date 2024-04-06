document.addEventListener('DOMContentLoaded', function() {
    // Variable to keep track of the last checked checkbox
    let lastChecked = null;

    function handleCheckboxClick(e) {
        // Check if the shift key was down AND check that the checkbox is being checked, not unchecked
        if (e.shiftKey && this.checked) {
            let inBetween = false;
            const checkboxes = document.querySelectorAll('.file-checkbox');

            // Loop over every checkbox
            checkboxes.forEach(checkbox => {
                if (checkbox === this || checkbox === lastChecked) {
                    inBetween = !inBetween; // Start or stop checking checkboxes
                }

                // If we're in the range between the last checked and the current, check them
                if (inBetween) {
                    checkbox.checked = true;
                }
            });
        }

        lastChecked = this; // Set lastChecked to the current checkbox
    }

    // Attach the event listener to each checkbox
    document.querySelectorAll('.file-checkbox').forEach(checkbox =>
        checkbox.addEventListener('click', handleCheckboxClick));
});
