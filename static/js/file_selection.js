
function selectAllCheckboxes(selectAllCheckbox) {
    const allCheckboxes = document.querySelectorAll('.file-checkbox');
    allCheckboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
}

function getSelectedFileNames() {
    return Array.from(document.querySelectorAll('.file-checkbox:checked')).map(cb => cb.value);
}
