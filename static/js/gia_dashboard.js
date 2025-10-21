const clockBtn = document.getElementById("clockBtn");
const statusText = document.getElementById("statusText");
const successModal = new bootstrap.Modal(document.getElementById("clockSuccessModal"));
const errorModal = new bootstrap.Modal(document.getElementById("clockErrorModal"));
const successTime = document.getElementById("successTime");
const currentTimeDisplay = document.getElementById("currentTime"); // Global clock display reference

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
});

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
}

// --- Function to Load Records ---
async function loadRecords() {
  try {
    const userId = clockBtn.getAttribute('data-user-id');
    const response = await fetch(`/api/gia-data?user_id=${encodeURIComponent(userId)}`);

    if (!response.ok) {
      throw new Error(`Failed to load records: ${response.status}`);
    }

    const records = await response.json();
    const tbody = document.getElementById('activityTableBody');
    tbody.innerHTML = '';

    // ... table population logic ...

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

// --- Handle Clock In/Out Event Listener ---
clockBtn.addEventListener("click", async () => {
  clockBtn.disabled = true; // Prevent double-clicking

  const now = new Date();
  const time = now.toLocaleTimeString();
  const userId = clockBtn.getAttribute('data-user-id');

  // Determine action based on CURRENT global state
  const endpoint = isClockedIn ? '/api/clock-out' : '/api/clock-in';
  const actionText = isClockedIn ? 'Clock Out' : 'Clock In';

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userId )
    });

    const data = await res.json();

    if (data.success) {
      // Update modal content and show
      document.getElementById("successTitle").textContent = `${actionText} Successful!`;
      successTime.textContent = time;
      document.getElementById("successMessage").innerHTML = 
        `You ${actionText.toLowerCase()} at <span class="fw-bold">${time}</span>.`;
      successModal.show();

      // Refresh data and status after successful action
      await loadRecords();
      await checkButton(); // This fetches the new status and updates global state
    } else {
      // Show error modal
      document.getElementById("errorTitle").textContent = `${actionText} Failed!`;
      document.getElementById("errorMessage").textContent =
        data.error || `Unable to record your ${actionText.toLowerCase()}. Please try again.`;
      errorModal.show();
    }
  } catch (err) {
    console.error("Clock in/out error:", err);
    document.getElementById("errorTitle").textContent = "Network Error";
    document.getElementById("errorMessage").textContent = "Unable to reach the server.";
    errorModal.show();
  } finally {
    clockBtn.disabled = false; // Re-enable button
  }
  // REMOVED: isClockedIn = !isClockedIn;
  // State is now controlled by the server via checkButton()
});