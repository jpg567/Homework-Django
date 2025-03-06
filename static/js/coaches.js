
// function clearFile() {
//     document.getElementById('fileInput').value = ''; // Clear the file input
// }
document.getElementById('form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    const formData = new FormData(this);
    const csrfToken = formData.get('csrfmiddlewaretoken'); // Get CSRF token

    fetch("/apolonYar/api/apolon_yar/create/", {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken, // Include CSRF token in headers
            'Accept': 'application/json',
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                // Handle errors
                const errorMessage = data.message || "An error occurred. Please try again.";
                document.getElementById('response-message').innerHTML = `<div class="alert alert-danger">${errorMessage}</div>`;
            });
        }
        return response.json();
    })
    .then(data => {
        // Handle success
        document.getElementById('response-message').innerHTML = `<div class="alert alert-success">${data.message}</div>`;
        // Optionally, close the modal or reset the form
        // $('#myModal').modal('hide'); // Uncomment if using jQuery
        // this.reset(); // Reset the form
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('response-message').innerHTML = `<div class="alert alert-danger">An unexpected error occurred. Please try again.</div>`;
    });
});

document.getElementById('student-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    const formData = new FormData(this);
    const csrfToken = formData.get('csrfmiddlewaretoken'); // Get CSRF token

    fetch("/apolonYar/api/student/create/", {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken, // Include CSRF token in headers
            'Accept': 'application/json',
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                // Handle errors
                const errorMessage = data.message || "An error occurred. Please try again.";
                document.getElementById('response-message-2').innerHTML = `<div class="alert alert-danger">${errorMessage}</div>`;
            });
        }
        return response.json();
    })
    .then(data => {
        // Handle success
        document.getElementById('response-message-2').innerHTML = `<div class="alert alert-success">${data.message}</div>`;
        // Optionally, close the modal or reset the form
        // $('#submit-lead').modal('hide'); // Uncomment if using jQuery
        // this.reset(); // Reset the form
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('response-message-2').innerHTML = `<div class="alert alert-danger">An unexpected error occurred. Please try again.</div>`;
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const homeworkLinks = document.querySelectorAll('.file-link');
    const homeworkWeeksList = document.getElementById('homework-weeks-list');

    homeworkLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default link behavior
            const studentId = this.getAttribute('data-student-id'); // Get the student ID
            const homeworkWeeks = this.getAttribute('data-homework-weeks').split(', '); // Get the homework weeks
            console.log(studentId, homeworkWeeks);
            homeworkWeeksList.innerHTML = ''; // Clear previous weeks

            homeworkWeeks.forEach(week => {
                const lastChar = week.slice(-1); // Get the last character of the week string
                const li = document.createElement('tr');
                li.innerHTML = `<td>هفته ${lastChar}</td>
                                <td>
                                    <a href="/apolonYar/student-homework/${studentId}/week/${lastChar}/" class="file-link" target="_blank">فایل</a>
                                </td>`;
                homeworkWeeksList.appendChild(li);
            });
        });
    });
});

        
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function submitScore(homeworkId) { // Pass homeworkId as a parameter
    const scoreSelect = document.getElementById('scoreSelect');
    const selectedScore = scoreSelect.value;
    console.log(selectedScore)
    if (selectedScore === "نمره هنرجو") {
        alert("لطفاً یک نمره انتخاب کنید."); // Alert if no score is selected
        return;
    }

    const formData = new FormData();
    formData.append('score', selectedScore);
    formData.append('homework_id', homeworkId); // Append the homework ID
    console.log(formData)
    fetch('/apolonYar/api/submit/score/', { // Use the correct API endpoint
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken') // Include CSRF token if needed
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Network response was not ok.');
    })
    .then(data => {
        console.log('Success:', data);
        // Handle success (e.g., show a success message)
    })
    .catch(error => {
        console.error('Error:', error);
        // Handle error (e.g., show an error message)
    });
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('edit-form').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission
        // document.getElementById('full_name').value = "Test Name"; // Hardcoded value
        // document.getElementById('phone').value = "1234567890"; // Hardcoded value

        const coachId = document.getElementById('coach_id').value;
        const fullName = document.getElementById('new_full_name').value;
        const phone = document.getElementById('new_phone').value;
        const profile = document.getElementById('profile').files[0]
        
        const formData = new FormData();
        formData.append('full_name', fullName);
        formData.append('phone', phone);
        if (profile) {
            formData.append('profile', profile); // Append the file
        }

        console.log('Coach ID:', coachId);
        console.log('Full Name:', fullName);
        console.log('Phone:', phone);

        fetch(`/apolonYar/api/coaches/${coachId}/edit/`, {
            method: 'PUT', // Use PUT for updating
            headers: {
                // 'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        })
        .then(response => {
            const responseMessage = document.getElementById('edit-response-message');
            if (response.status === 200) { // Check for a successful response
                return response.json().then(data => {
                    responseMessage.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                    // Optionally close the modal or reset the form
                    // $('#edit-profile').modal('hide'); // If using jQuery
                    document.getElementById('edit-form').reset(); // Reset form fields
                });
            } else {
                return response.json().then(data => {
                    responseMessage.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('edit-response-message').innerHTML = `<div class="alert alert-danger">${error}</div>`;
        });
    });
});
