document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('report-generation-form');
    const generateButton = document.getElementById('generate-report-button');
    const progressDisplay = document.getElementById('progress-display');
    const toastMessageDiv = document.getElementById('toast-message');
    let progressInterval;

    // Function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Function to show toast message
    function showToast(message, type = 'info') {
        toastMessageDiv.textContent = message;
        toastMessageDiv.className = 'toast-message show '; // Reset and add show class
        if (type === 'success') {
            toastMessageDiv.classList.add('success');
        } else if (type === 'error') {
            toastMessageDiv.classList.add('error');
        }
        setTimeout(() => {
            toastMessageDiv.classList.remove('show');
        }, 3000); // Hide after 3 seconds
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        generateButton.disabled = true;
        progressDisplay.style.display = 'block';
        progressDisplay.className = ''; // Clear previous classes
        progressDisplay.textContent = '리포트 생성 요청 중...';

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const taskId = data.task_id;
                progressDisplay.textContent = data.message + ' (ID: ' + taskId + ')';
                startPolling(taskId);
            } else {
                progressDisplay.classList.add('error');
                progressDisplay.textContent = '오류: ' + data.message;
                generateButton.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            progressDisplay.classList.add('error');
            progressDisplay.textContent = '리포트 생성 요청 중 네트워크 오류가 발생했습니다.';
            generateButton.disabled = false;
        });
    });

    function startPolling(taskId) {
        progressInterval = setInterval(() => {
            fetch(`/get_report_progress/?task_id=${taskId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'completed') {
                        progressDisplay.classList.add('success');
                        progressDisplay.textContent = data.message + ' 페이지를 새로고침하여 리포트를 확인하세요.';
                        clearInterval(progressInterval);
                        generateButton.disabled = false;
                        // Optionally, refresh the page or update the report list
                        setTimeout(() => location.reload(), 2000); 
                    } else if (data.status === 'failed') {
                        progressDisplay.classList.add('error');
                        progressDisplay.textContent = data.message;
                        clearInterval(progressInterval);
                        generateButton.disabled = false;
                    } else {
                        progressDisplay.textContent = data.message + ' (' + data.stage + ')';
                    }
                })
                .catch(error => {
                    console.error('Polling error:', error);
                    progressDisplay.classList.add('error');
                    progressDisplay.textContent = '진행 상황을 가져오는 중 오류가 발생했습니다.';
                    clearInterval(progressInterval);
                    generateButton.disabled = false;
                });
        }, 2000); // Poll every 2 seconds
    }

    // Delete Report functionality
    document.querySelectorAll('.delete-button').forEach(button => {
        button.addEventListener('click', function() {
            const reportId = this.dataset.reportId;
            if (confirm('정말로 이 리포트를 삭제하시겠습니까?')) {
                fetch(`/reports/${reportId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json' // Important for Django's CSRF to work with non-form data
                    },
                    body: JSON.stringify({})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        document.getElementById(`report-item-${reportId}`).remove();
                        showToast(data.message, 'success');
                    } else {
                        showToast('리포트 삭제 실패: ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    console.error('Delete error:', error);
                    showToast('리포트 삭제 중 네트워크 오류가 발생했습니다.', 'error');
                });
            }
        });
    });
});