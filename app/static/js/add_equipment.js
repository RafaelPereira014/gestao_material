function toggleEntryMode() {
    const singleEntryFields = document.getElementById("singleEntryFields");
    const bulkEntryFields = document.getElementById("bulkEntryFields");
    const isBulk = document.getElementById("bulkEntry").checked;

    singleEntryFields.style.display = isBulk ? "none" : "block";
    bulkEntryFields.style.display = isBulk ? "block" : "none";
}

function showSnackbar() {
    const snackbar = document.getElementById("snackbar");
    snackbar.className = "show"; // Add the "show" class to div
    setTimeout(() => { snackbar.className = snackbar.className.replace("show", ""); }, 3000); // After 3 seconds, remove the "show" class
}