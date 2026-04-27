const clockBtn = document.getElementById("clockBtn");
const statusText = document.getElementById("statusText");
const successModal = new bootstrap.Modal(document.getElementById("clockSuccessModal"));
const errorModal = new bootstrap.Modal(document.getElementById("clockErrorModal"));
const successTime = document.getElementById("successTime");
const currentTimeDisplay = document.getElementById("currentTime");
const monthFilter = document.getElementById("monthFilter");

let isClockedIn = false;
let is_grace = false;

// Variables for Live Progress Tracking
let baseTodayHours = 0;
let activeClockInTime = null;
let liveProgressInterval = null;

document.addEventListener('DOMContentLoaded', async () => {
    const updateClock = () => {
        const now = new Date();
        currentTimeDisplay.textContent = now.toLocaleTimeString();
    };

    updateClock();
    setInterval(updateClock, 1000);

    await loadRecords();
    await checkButton();
    manageLiveProgress(); // Start the live tracker on load
    // await betaPopupCheck();
});

async function checkButton() {
    const userId = clockBtn.getAttribute('data-user-id');
    try {
        const res = await fetch(`/api/status?user_id=${userId}`);
        const data = await res.json();

        isClockedIn = data.clocked_in && !data.clocked_out;
        is_grace = data.is_grace;

        clockBtn.innerHTML = isClockedIn && !is_grace
            ? '<i class="fas fa-stop me-2"></i>Clock Out'
            : '<i class="fas fa-play me-2"></i>Clock In';

        if (isClockedIn && !is_grace) {
            statusText.textContent = 'Clocked In';
            statusText.style.color = "#059669";
        } else {
            statusText.textContent = 'Clocked Out';
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

        const totalRendered = parseFloat(summary.total_hours || 0);
        const targetHours = parseFloat(summary.target_hours || 60);

        // Save the base hours completed today (excluding the active running shift)
        baseTodayHours = parseFloat(summary.today_hours) || 0;
        const activeDays = parseInt(summary.active_days || 0);
        const remainingHours = Math.max(0, targetHours - totalRendered);

        document.getElementById('summaryTotalHours').innerText = totalRendered.toFixed(2);
        const targetEl = document.getElementById('targetHours');
        if (targetEl) targetEl.innerText = targetHours;
        document.getElementById('summaryRemaining').innerText = remainingHours.toFixed(2);
        document.getElementById('summaryActiveDays').innerText = activeDays;

        // Reset active clock in time
        activeClockInTime = null;

        if (records && records.length > 0) {
            // Check if the most recent record is an active shift (has clock_in but no clock_out)
            const latest = records[0];
            if (latest.clock_in && (!latest.clock_out || latest.clock_out === '-')) {
                activeClockInTime = latest.clock_in; // e.g., "14:30:00"
            }

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
        errorModal.show();
    }
}

// --- NEW FUNCTION: Live Progress Tracker ---
function manageLiveProgress() {
    if (liveProgressInterval) clearInterval(liveProgressInterval);

    const summaryTodayEl = document.getElementById('summaryToday');

    const updateProgress = () => {
        if (isClockedIn && activeClockInTime) {
            // Parse the clock-in time string (assumes 24h format like "14:30:00")
            const now = new Date();
            const [hours, minutes, seconds] = activeClockInTime.split(':').map(Number);

            const clockInDate = new Date();
            clockInDate.setHours(hours, minutes, seconds || 0, 0);

            let diffMs = now - clockInDate;
            if (diffMs < 0) diffMs = 0; // Sanity check for edge cases

            // Convert milliseconds to decimal hours
            const liveSessionHours = diffMs / (1000 * 60 * 60);
            const totalLive = baseTodayHours + liveSessionHours;

            summaryTodayEl.innerText = totalLive.toFixed(2);
        } else {
            // If not clocked in, just show the static base hours from the database
            summaryTodayEl.innerText = baseTodayHours.toFixed(2);
        }
    };

    updateProgress(); // Run immediately
    liveProgressInterval = setInterval(updateProgress, 10000); // Update the visual every 10 seconds
}

clockBtn.addEventListener("click", async () => {
    clockBtn.disabled = true;

    const now = new Date();
    const time = now.toLocaleTimeString();
    const userId = clockBtn.getAttribute('data-user-id');

    const endpoint = isClockedIn && !is_grace
        ? '/api/clock-out'
        : '/api/clock-in';

    const actionText = isClockedIn && !is_grace
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
            manageLiveProgress(); // Restart/Update the tracker based on new state
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
        errorMessage.textContent = "Unable to reach the server. Reloading in seconds...";

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
});

function showPage() {
    const main = document.querySelector('.main-container');
    main.style.display = 'block';
    main.classList.add('visible');
}

const betaPopupCheck = async () => {
    const isFirstVisit = localStorage.getItem('betaNoticeShown') !== 'true';

    if (isFirstVisit) {
        const betaModal = new bootstrap.Modal(document.getElementById('betaNoticeModal'));
        betaModal.show();

        localStorage.setItem('betaNoticeShown', 'true');
    }
};

// --- NEW FUNCTION: Live Progress Tracker ---
function manageLiveProgress() {
    if (liveProgressInterval) clearInterval(liveProgressInterval);

    const summaryTodayEl = document.getElementById('summaryToday');

    // Helper to safely parse both "14:30" and "02:30 PM" formats
    const parseTimeStr = (timeStr) => {
        if (!timeStr) return null;

        // Regex to extract hours, minutes, seconds, and AM/PM
        const match = String(timeStr).match(/(\d+):(\d+)(?::(\d+))?\s*(AM|PM)?/i);
        if (!match) return null;

        let hours = parseInt(match[1], 10);
        const minutes = parseInt(match[2], 10);
        const seconds = match[3] ? parseInt(match[3], 10) : 0;
        const ampm = match[4] ? match[4].toUpperCase() : null;

        // Convert 12-hour to 24-hour format if AM/PM is present
        if (ampm === 'PM' && hours < 12) hours += 12;
        if (ampm === 'AM' && hours === 12) hours = 0;

        const d = new Date();
        d.setHours(hours, minutes, seconds, 0);
        return d;
    };

    const updateProgress = () => {
        // Ensure baseTodayHours is a safe number
        const safeBaseHours = parseFloat(baseTodayHours) || 0;

        if (isClockedIn && activeClockInTime && activeClockInTime !== '-') {
            const now = new Date();
            const clockInDate = parseTimeStr(activeClockInTime);

            if (clockInDate) {
                let diffMs = now - clockInDate;
                if (diffMs < 0) diffMs = 0; // Prevent negative time if clock is weird

                // Convert milliseconds to decimal hours
                const liveSessionHours = diffMs / (1000 * 60 * 60);
                const totalLive = safeBaseHours + liveSessionHours;

                summaryTodayEl.innerText = totalLive.toFixed(2);
                return;
            }
        }

        // If not clocked in (or time parsing fails), fallback to static hours
        summaryTodayEl.innerText = safeBaseHours.toFixed(2);
    };

    updateProgress(); // Run immediately
    liveProgressInterval = setInterval(updateProgress, 10000); // Update every 10 seconds
}

document.addEventListener('DOMContentLoaded', function() {
    const scheduleModal = document.getElementById('scheduleModal');
    
    if (scheduleModal) {
        scheduleModal.addEventListener('show.bs.modal', async function(event) {
            // Button that triggered the modal
            const button = event.relatedTarget;
            const userId = button.getAttribute('data-user-id');
            const container = document.getElementById('scheduleListContainer');
            
            // Show loading state
            container.innerHTML = `
                <div class="text-center text-muted my-3">
                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                    Loading schedule...
                </div>
            `;

            try {
                // Fetch the schedule
                const response = await fetch(`/api/get-schedule/${userId}`);
                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(data.error || 'Failed to fetch schedule');
                }

                if (!data.schedules || data.schedules.length === 0) {
                    container.innerHTML = `
                        <div class="alert alert-light text-center border">
                            No schedule assigned yet.
                        </div>`;
                    return;
                }

                // Build the HTML list
                let listHtml = '<ul class="list-group list-group-flush border rounded-3">';
                
                // Optional: Map to sort days correctly if they don't come back sorted
                const dayOrder = { "Monday":1, "Tuesday":2, "Wednesday":3, "Thursday":4, "Friday":5, "Saturday":6, "Sunday":7 };
                data.schedules.sort((a, b) => dayOrder[a.day] - dayOrder[b.day]);

                data.schedules.forEach(sched => {
                    let timeText = '';
                    let badgeClass = 'bg-primary';

                    if (!sched.start_time || !sched.end_time) {
                        timeText = 'Rest Day';
                        badgeClass = 'bg-secondary';
                    } else if (sched.is_split_shift) {
                        // Handle Split Shifts
                        timeText = `${formatTime(sched.start_time)} - ${formatTime(sched.end_time)} <br> ${formatTime(sched.split_start_time)} - ${formatTime(sched.split_end_time)}`;
                        badgeClass = 'bg-info text-dark';
                    } else {
                        // Regular Shift
                        timeText = `${formatTime(sched.start_time)} - ${formatTime(sched.end_time)}`;
                    }

                    listHtml += `
                        <li class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <div>
                                <span class="fw-semibold d-block text-dark">${sched.day}</span>
                                <span class="text-muted small">${sched.is_split_shift ? 'Split Shift' : (timeText === 'Rest Day' ? 'Rest Day' : 'Regular Shift')}</span>
                            </div>
                            <span class="badge ${badgeClass} rounded-pill px-3 py-2 text-wrap text-end" style="max-width: 150px; line-height: 1.4;">
                                ${timeText}
                            </span>
                        </li>
                    `;
                });

                listHtml += '</ul>';
                container.innerHTML = listHtml;

            } catch (error) {
                console.error("Error loading schedule:", error);
                container.innerHTML = `
                    <div class="alert alert-danger text-center">
                        <i class="fas fa-exclamation-circle me-1"></i>
                        Could not load schedule. Please try again.
                    </div>
                `;
            }
        });
    }

    // Helper function to convert 24hr time (HH:MM) to 12hr AM/PM format
    function formatTime(timeStr) {
        if (!timeStr) return '';
        const [hourString, minute] = timeStr.split(':');
        let hour = parseInt(hourString, 10);
        const ampm = hour >= 12 ? 'PM' : 'AM';
        hour = hour % 12 || 12; // Convert '0' to '12' for midnight
        return `${hour}:${minute} ${ampm}`;
    }
});