const API_URL = "http://127.0.0.1:8000";

// --- 1. LOGIN LOGIC ---
async function handleLogin() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    // FastAPI's OAuth2PasswordRequestForm expects data in x-www-form-urlencoded format
    const formData = new URLSearchParams();
    formData.append('username', email); // form_data.username in your login route
    formData.append('password', password);

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            body: formData // Content-Type is set automatically by URLSearchParams
        });

        const data = await response.json();

        if (response.ok) {
            // Save token to localStorage for persistent sessions
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('userEmail', data.user_email);
            showDashboard();
        } else {
            alert(data.detail || "Login failed. Check your credentials.");
        }
    } catch (err) {
        console.error("Connection error:", err);
    }
}

// --- 2. PROTECTED DATA FETCHING ---
async function fetchMedications() {
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch(`${API_URL}/medications/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const meds = await response.json();
            renderMedications(meds, 'med-list');
        }
    } catch (err) {
        console.error("Fetch error:", err);
    }
}

async function fetchArchivedMedications() {
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch(`${API_URL}/medications/archived`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const meds = await response.json();
            renderMedications(meds, 'archived-med-list');
        }
    } catch (err) {
        console.error("Fetch archived error:", err);
    }
}

// --- 3. UI MANAGEMENT ---
function renderMedications(meds, listId) {
    const list = document.getElementById(listId);
    const dropdown = document.getElementById('rem-med-id');
    
    // Only update dropdown if rendering active meds
    if (listId === 'med-list') {
        dropdown.innerHTML = '<option value="">-- Choose a Medication --</option>'; 
        meds.forEach(m => {
            if (!m.archived) {
                const option = document.createElement('option');
                option.value = m.id;
                option.textContent = `${m.name} (${m.dosage})`;
                dropdown.appendChild(option);
            }
        });
    }
    
    list.innerHTML = ""; // Clear existing items

    meds.forEach(m => {
        const li = document.createElement('li');
        
        // This logic checks the 'archived' status from your MySQL database
        const actionButton = m.archived 
            ? `<button onclick="handleUnarchiveMedication(${m.id})" class="btn-success">Unarchive</button>` 
            : `<button onclick="handleArchiveMedication(${m.id})" class="btn-warning">Archive</button>`;

        li.innerHTML = `
            <div class="med-item">
                <span>
                    <strong>${m.name}</strong> - ${m.dosage} 
                    ${m.archived ? '<b style="color:red;">[ARCHIVED]</b>' : ''}
                </span>
                <div class="actions">
                    ${actionButton}
                    <button onclick="handleEditMedication(${m.id}, '${m.name.replace(/'/g, "\\'")}', '${m.dosage.replace(/'/g, "\\'")}')" class="btn-secondary">Edit</button>
                    <button onclick="handleDeleteMedication(${m.id})" class="btn-danger">Delete</button>
                </div>
            </div>
        `;
        list.appendChild(li);
    });
}
function showDashboard() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    fetchMedications();
    fetchArchivedMedications();
}

function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    location.reload(); // Refresh to reset UI state
}

// --- 4. INITIALIZATION ---
// Check if user is already logged in on page load
window.onload = () => {
    if (localStorage.getItem('token')) {
        showDashboard();
    }
};

async function handleAddMedication() {
    const name = document.getElementById('med-name').value;
    const dosage = document.getElementById('med-dosage').value;
    const token = localStorage.getItem('token');

    const medData = { name, dosage, archived: false };

    try {
        const response = await fetch(`${API_URL}/medications/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(medData)
        });

        if (response.ok) {
            alert("Medication added successfully!");
            fetchMedications();
            fetchArchivedMedications();
        }
    } catch (err) {
        console.error("Failed to add medication:", err);
    }
}

// --- CREATE REMINDER ---
async function handleCreateReminder() {
    const token = localStorage.getItem('token');
    const reminderData = {
        medication_id: parseInt(document.getElementById('rem-med-id').value),
        name: document.getElementById('rem-name').value,
        reminder_time: new Date(document.getElementById('rem-time').value).toISOString(),
        frequency: document.getElementById('rem-freq').value, // e.g., "DAILY"
        message: document.getElementById('rem-msg').value
    };

    const response = await fetch(`${API_URL}/reminders/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(reminderData)
    });

    if (response.ok) {
        alert("Reminder set!");
    }
}

async function handleArchiveMedication(medId) {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`${API_URL}/medications/archive/${medId}`, {
            method: 'PUT', // Your route uses @router.delete for archiving
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            alert("medication archived");
            fetchMedications();
            fetchArchivedMedications();
        }
    } catch (err) {
        console.error("Archive error:", err);
    }
}
async function handleUnarchiveMedication(medId) {
    const token = localStorage.getItem('token');
    
    // This JSON body matches your MedicationUpdate Pydantic schema
    const updateData = { archived: false };

    try {
        const response = await fetch(`${API_URL}/medications/${medId}`, {
            method: 'PUT', // Matches @router.put("/{med_id}") in your backend
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData)
        });

        if (response.ok) {
            console.log("Medication restored!");
            fetchMedications();
            fetchArchivedMedications();
        } else {
            const err = await response.json();
            alert("Error: " + err.detail);
        }
    } catch (err) {
        console.error("Connection failed:", err);
    }
}

async function fetchReminders() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`${API_URL}/reminders/0`, { // '0' is a placeholder as backend uses current_user
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const reminders = await response.json();
            const list = document.getElementById('reminder-list');
            list.innerHTML = reminders.map(r => `
                <li>
                    <strong>${r.name}:</strong> ${new Date(r.reminder_time).toLocaleString()} 
                    <p>${r.message}</p>
                </li>
            `).join('');
        }
    } catch (err) {
        console.error("Reminder fetch error:", err);
    }
    
}
async function fetchMotivation(params) {
    const response = await fetch(`${API_URL}/motivation/random`);
    if(response.ok){
        const text = await response.json();
        document.getElementById('motivation-display').innerText = text
    }
}

// --- 1. PERMANENT MEDICATION DELETION ---
// Targets: DELETE /medications/{med_id}
async function handleDeleteMedication(medId) {
    if (!confirm("Are you sure you want to permanently delete this medication?")) return;

    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`${API_URL}/medications/${medId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            alert("Medication deleted successfully.");
            fetchMedications();
            fetchArchivedMedications();
        } else {
            const err = await response.json();
            alert(err.detail || "Failed to delete medication.");
        }
    } catch (err) {
        console.error("Delete Med Error:", err);
    }
}

// --- 2. UPDATE MEDICATION ---
async function handleEditMedication(medId, currentName, currentDosage) {
    const newName = prompt("Enter new name:", currentName);
    if (newName === null) return;
    const newDosage = prompt("Enter new dosage:", currentDosage);
    if (newDosage === null) return;

    const token = localStorage.getItem('token');
    const updateData = { name: newName, dosage: newDosage };

    try {
        const response = await fetch(`${API_URL}/medications/${medId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData)
        });

        if (response.ok) {
            alert("Medication updated!");
            fetchMedications();
            fetchArchivedMedications();
        } else {
            const err = await response.json();
            alert("Error: " + err.detail);
        }
    } catch (err) {
        console.error("Update error:", err);
    }
}

// --- 2. UPDATE REMINDER ---
// Targets: PATCH /reminders/{reminder_id}
async function handleUpdateReminder(reminderId) {
    const token = localStorage.getItem('token');
    
    // We only send the fields that need updating (partial update)
    const updateData = {
        reminder_time: document.getElementById('update-rem-time').value ? 
            new Date(document.getElementById('update-rem-time').value).toISOString() : undefined,
        message: document.getElementById('update-rem-msg').value || undefined,
        isTaken: document.getElementById('update-rem-taken').checked
    };

    // Remove undefined keys so we don't overwrite with nulls
    Object.keys(updateData).forEach(key => updateData[key] === undefined && delete updateData[key]);

    try {
        const response = await fetch(`${API_URL}/reminders/${reminderId}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData)
        });

        if (response.ok) {
            alert("Reminder updated!");
            fetchReminders();
        } else {
            const err = await response.json();
            alert(err.detail || "Update failed.");
        }
    } catch (err) {
        console.error("Update Reminder Error:", err);
    }
}