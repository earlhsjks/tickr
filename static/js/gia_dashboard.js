const clockBtn = document.getElementById("clockBtn");
const statusText = document.getElementById("statusText");
const successModal = new bootstrap.Modal(document.getElementById("clockSuccessModal"));
const errorModal = new bootstrap.Modal(document.getElementById("clockErrorModal"));
const successTime = document.getElementById("successTime");
const currentTimeDisplay = document.getElementById("currentTime"); // Global clock display reference
const monthFilter = document.getElementById("monthFilter");

let isClockedIn = false;

document.addEventListener('DOMContentLoaded', async () => {
    const updateClock = () => {
        const now = new Date();
        currentTimeDisplay.textContent = now.toLocaleTimeString();
    };

    updateClock();
    setInterval(updateClock, 1000);

    await loadRecords();
    await checkButton();
    await betaPopupCheck()
;});

async function checkButton() {
    const userId = clockBtn.getAttribute('data-user-id');
    try {
        const res = await fetch(`/api/status?user_id=${userId}`);
        const data = await res.json();

        isClockedIn = data.clocked_in && !data.clocked_out;
        is30min = data.is30min;

        clockBtn.innerHTML = isClockedIn && !is30min
            ? '<i class="fas fa-stop me-2"></i>Clock Out'
            : '<i class="fas fa-play me-2"></i>Clock In';

        if (isClockedIn && !is30min) {
            statusText.textContent = 'Clocked In'
            statusText.style.color = "#059669";
        } else {
            statusText.textContent = 'Clocked Out'
            statusText.style.color = "";
        }
    } catch (err) {
        console.error('Error checking button status:', err);
        statusText.textContent = "Status Check Failed";
        clockBtn.disabled = true;
        clockBtn.style.background = "gray";
    }

    showPage();
}

// --- Function to Load Records ---
async function loadRecords() {
    try {
        const userId = clockBtn.getAttribute('data-user-id');
        const month = monthFilter.value;
        const response = await fetch(
        `/api/gia-data?user_id=${encodeURIComponent(userId)}&month=${encodeURIComponent(month)}`
        );
        if (!response.ok) {
            throw new Error(`Failed to load records: ${response.status}`);
        }

        const data = await response.json();
        const records = data.records;
        const summary = data.summary;
        const tbody = document.getElementById('activityTableBody');
        tbody.innerHTML = '';

        // Summaries
        document.getElementById('summaryHours').innerText = summary.total_hours;
        document.getElementById('summaryOnTime').innerText = summary.total_on_time;
        document.getElementById('summaryLate').innerText = summary.total_late;
        document.getElementById('summaryAbsences').innerText = summary.total_absences;

        // Simplified record rendering
        if (records && records.length > 0) {
            records.forEach(record => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
              <td class="text-center">${record.date || '-'}</td>
              <td class="text-center">${record.clock_in || '-'}</td>
              <td class="text-center">${record.clock_out || '-'}</td>
              <td class="text-center">${record.total_hours || '-'}</td>
            `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-3">No records found</td></tr>`;
        }

    } catch (err) {
        console.error('Error loading records:', err);
        document.getElementById("errorTitle").textContent = "Error Loading Records";
        document.getElementById("errorMessage").textContent = "Could not fetch data. Please try again.";
        errorModal.show(); // Use global errorModal
    }
}

clockBtn.addEventListener("click", async () => {
    clockBtn.disabled = true;

    const now = new Date();
    const time = now.toLocaleTimeString();
    const userId = clockBtn.getAttribute('data-user-id');

    const endpoint = isClockedIn && !is30min 
    ? '/api/clock-out' 
    : '/api/clock-in';
    
    const actionText = isClockedIn && !is30min 
    ? 'Clock Out' 
    : 'Clock In';

    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userId)
        });

        const data = await res.json();

        if (data.success) {
            document.getElementById("successTitle").textContent = `${actionText} Successful!`;
            successTime.textContent = time;
            document.getElementById("successMessage").innerHTML =
                `You ${actionText.toLowerCase()} at <span class="fw-bold">${data.data.time_record}</span>.`;
            successModal.show();

            await loadRecords();
            await checkButton();
        } else {
            document.getElementById("errorTitle").textContent = `${actionText} Failed!`;
            document.getElementById("errorMessage").textContent =
                data.error || `Unable to record your ${actionText.toLowerCase()}. Please try again.`;
            errorModal.show();
        }
    } catch (err) {
        console.error("Clock in/out error:", err);
        
        const errorTitle = document.getElementById("errorTitle");
        const errorMessage = document.getElementById("errorMessage");
        
        errorTitle.textContent = "Network Error";
        errorMessage.textContent = "Unable to reach the server. Reloading in 5 seconds...";

        errorModal.show();

        let countdown = 6;
        const interval = setInterval(() => {
            countdown--;
            if (countdown > 0) {
                errorMessage.textContent = `Unable to reach the server. Reloading in ${countdown} second${countdown === 1 ? '' : 's'}...`;
            } else {
                clearInterval(interval);
                window.location.reload();
            }
        }, 1000);
    } finally {
        clockBtn.disabled = false;
    }
});

monthFilter.addEventListener("change", () => {
    loadRecords();
})

function showPage() {
    const main = document.querySelector('.main-container');
    main.style.display = 'block';
    main.classList.add('visible');
}

betaPopupCheck = async () => {
    const isFirstVisit = localStorage.getItem('betaNoticeShown') !== 'true';

    if (isFirstVisit) {
        const betaModal = new bootstrap.Modal(document.getElementById('betaNoticeModal'));
        betaModal.show();

        localStorage.setItem('betaNoticeShown', 'true');
    }
}