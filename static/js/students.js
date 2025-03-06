function loadPictures(weekNumber) {
    fetch(`/student/api/homework/?week_number=${weekNumber}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const picturesContainer = document.getElementById(`pictures-container-${weekNumber}`);
            const uploadContainer = document.getElementById(`upload-container-${weekNumber}`);
            
            // Clear previous pictures
            picturesContainer.innerHTML = ''; 

            if (data.has_pictures) {
                data.pictures.forEach((url, index) => {
                    // Create a new table row for the label and image
                    const pictureRow = document.createElement('tr');

                    // Create a cell for the label
                    const labelCell = document.createElement('td');
                    const label = document.createElement('span');
                    label.textContent = `عکس ${index + 1}`; // Create label for each picture
                    labelCell.appendChild(label);
                    pictureRow.appendChild(labelCell);

                    // Create a cell for the image
                    const imageCell = document.createElement('td');
                    const img = document.createElement('img');
                    img.src = url;
                    img.alt = 'Uploaded Image';
                    img.style.maxWidth = '100px';
                    img.style.maxHeight = '100px';

                    // Add click event to open image in a new tab
                    img.addEventListener('click', () => {
                        window.open(url, '_blank'); // Open the image URL in a new tab
                    });

                    imageCell.appendChild(img);
                    pictureRow.appendChild(imageCell);

                    // Append the row to the pictures container
                    picturesContainer.appendChild(pictureRow);
                });
                uploadContainer.style.display = 'none'; // Hide upload input if pictures exist
            } else {
                uploadContainer.style.display = 'block'; // Show upload input if no pictures
            }
        })
        .catch(error => console.error('Error loading pictures:', error));
}
// Call loadPictures when the modal is shown
document.addEventListener('DOMContentLoaded', function() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            const weekNumber = this.id.split('-')[1];
            loadPictures(weekNumber);
        });
    });
});

function deleteAllPictures(weekNumber) {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Check if this cookie string begins with the name we want
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    // First, load the pictures for the specified week
    fetch(`/student/api/homework/?week_number=${weekNumber}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // Return the parsed JSON
        })
        .then(data => {
            const pictures = data.pictures || []; // Get the pictures array from the response
            console.log(pictures)
            if (pictures.length === 0) {
                alert('هیچ عکسی برای حذف وجود ندارد.');
                return;
            }

            if (confirm('آیا مطمئن هستید که می‌خواهید همه عکس‌ها را حذف کنید؟')) {
                fetch('/student/api/delete/picture/', {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken') // Ensure you include CSRF token if required
                    },
                    body: JSON.stringify({
                        week_number: weekNumber,
                        pictures: pictures // Assuming 'pictures' is an array of picture URLs
                    })
                })                        
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log(data.message); // Handle success message
                    loadPictures(weekNumber); // Reload pictures after deletion
                })
                .catch(error => console.error('Error deleting pictures:', error));
            }
        })
        .catch(error => console.error('Error loading pictures:', error));
}
function submitFiles(weekNumber) {
    const formData = new FormData();
    formData.append('week_number', weekNumber); // Append the week number

    // Select all file inputs and textareas within the specific modal for the given week number
    const fileInputs = document.querySelectorAll(`#file-${weekNumber} input[type="file"]`);
    const textareas = document.querySelectorAll(`#file-${weekNumber} textarea`);

    // Loop through each file input and append the files and their corresponding descriptions to the FormData
    fileInputs.forEach((input, index) => {
        if (input.files.length > 0) {
            formData.append('pictures', input.files[0]); // Append each file
            formData.append('descriptions', textareas[index].value); // Append the corresponding description
        }
    });

    console.log('Submitting FormData:', formData);

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Check if this cookie string begins with the name we want
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Send the FormData to the server
    fetch('/student/api/send/picture/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken') // Include CSRF token if needed
        }
    })
    .then(response => {
        console.log('Response:', response);
        return response.json();
    })
    .then(data => {
        console.log('Data:', data);
        // Check if the submission was successful
        if (data.success) { // Assuming your API returns a success field
            alert('Files submitted successfully!'); // Show success alert
            window.location.href = '/'; // Redirect to the home path
        } else {
            alert('Submission failed: ' + data.message); // Show error message if needed
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while submitting the files.'); // Show error alert
    });
}
