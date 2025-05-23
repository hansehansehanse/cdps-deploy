
// Handle form submission for dataset upload (without confirming overwrite)
document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    formData.append('force_upload', 'false'); // Initial check only

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.overlap) {
            // Show modal if overlapping records are found
            document.getElementById('overlap-count').innerText =
                `There are ${data.count} overlapping records. Do you want to proceed?`;
            const modal = new bootstrap.Modal(document.getElementById('overlapModal'));
            modal.show();
        } else if (data.success) {
            // alert("Dataset uploaded successfully!");
            location.reload();
        }
    })
    .catch(error => {
        console.error('Upload failed', error);
    });
});

// Handle confirm button in modal (when the user confirms overwrite)
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('confirmUploadBtn').addEventListener('click', function () {
        console.log("Confirm upload button clicked.");

        const form = document.getElementById('uploadForm');
        const formData = new FormData(form);
        formData.append('force_upload', 'true'); // Confirming overwrite

        console.log("Form data prepared with force_upload=true.");

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log("Server response data:", data);
            if (data.success) {
                // alert("Upload completed, overwriting old records.");
                const modal = bootstrap.Modal.getInstance(document.getElementById('overlapModal'));
                modal.hide();
                console.log("Modal hidden and page reloading.");
                location.reload();
            } else {
                console.warn("Upload response indicated failure:", data);
            }
        })
        .catch(error => {
            console.error('Upload failed', error);
        });
    });
});
