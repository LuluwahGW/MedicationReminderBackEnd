// Served by the backend itself -> same-origin (empty prefix). Opened via Live Server
// (port 5500) -> talk to the local backend explicitly.
const API_URL = location.port === "5500" ? "http://127.0.0.1:8000" : "";

// --- 0. AUTH TAB + MESSAGES ---
function showAuthTab(tab) {
    const isSignin = tab === 'signin';
    document.getElementById('signin-form').hidden = !isSignin;
    document.getElementById('signup-form').hidden = isSignin;
    document.getElementById('tab-signin').classList.toggle('is-active', isSignin);
    document.getElementById('tab-signup').classList.toggle('is-active', !isSignin);
    setAuthMessage('');
}

function setAuthMessage(text, isError = false) {
    const el = document.getElementById('auth-message');
    el.textContent = text;
    el.classList.toggle('is-error', isError);
}

// Turn FastAPI's error payload into a readable string.
function formatError(data, fallback) {
    if (Array.isArray(data?.detail)) {
        return data.detail
            .map(e => (e.msg || '').replace(/^Value error,\s*/, ''))
            .join('\n');
    }
    return data?.detail || fallback;
}

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
            setAuthMessage(formatError(data, "Login failed. Check your credentials."), true);
        }
    } catch (err) {
        console.error("Connection error:", err);
        setAuthMessage("Couldn't reach the server. Is the backend running?", true);
    }
}

// --- 1b. REGISTRATION LOGIC ---
async function handleRegister() {
    const name = document.getElementById('signup-name').value.trim();
    const email = document.getElementById('signup-email').value.trim();
    const password = document.getElementById('signup-password').value;

    try {
        const response = await fetch(`${API_URL}/users/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        const data = await response.json();

        if (response.ok) {
            // Registration succeeded — log the new user straight in.
            document.getElementById('login-email').value = email;
            document.getElementById('login-password').value = password;
            await handleLogin();
        } else {
            setAuthMessage(formatError(data, "Registration failed."), true);
        }
    } catch (err) {
        console.error("Registration error:", err);
        setAuthMessage("Couldn't reach the server. Is the backend running?", true);
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
const MED_ICON_COLORS = ['icon-yellow', 'icon-pink', 'icon-green'];

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

    meds.forEach((m, i) => {
        const li = document.createElement('li');
        const iconColor = MED_ICON_COLORS[i % MED_ICON_COLORS.length];
        
        // This logic checks the 'archived' status from your MySQL database
        const actionButton = m.archived 
            ? `<button onclick="handleUnarchiveMedication(${m.id})" class="btn-success">Unarchive</button>` 
            : `<button onclick="handleArchiveMedication(${m.id})" class="btn-warning">Archive</button>`;

        li.innerHTML = `
            <div class="med-item">
                <span class="med-icon ${iconColor}" aria-hidden="true"></span>
                <span class="med-info">
                    <strong>${m.name}</strong> - ${m.dosage} 
                    ${m.archived ? '<b class="archived-tag">[ARCHIVED]</b>' : ''}
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
    document.getElementById('logout-btn').hidden = false;
    document.getElementById('app-subtitle').textContent = 'medication list';
    fetchMedications();
    fetchArchivedMedications();
    fetchMotivation();
    fetchMyCaregivers();
    fetchMyPatients();
    loadPendingInvite();
}

function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    location.reload(); // Refresh to reset UI state
}

// --- 4. INITIALIZATION ---
// Check if user is already logged in on page load
window.onload = () => {
    captureInviteFromUrl();
    if (localStorage.getItem('token')) {
        showDashboard();
    } else if (sessionStorage.getItem('pendingInvite')) {
        setAuthMessage("You've been invited to be someone's caregiver. Sign in or create an account to review the invitation.");
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
    const reminderTime = new Date(document.getElementById('rem-time').value);
    if (Number.isNaN(reminderTime.getTime())) {
        alert("Please choose a valid reminder date and time.");
        return;
    }

    const reminderData = {
        medication_id: parseInt(document.getElementById('rem-med-id').value),
        name: document.getElementById('rem-name').value,
        reminder_time: reminderTime.toISOString(),
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
        const response = await fetch(`${API_URL}/reminders/`, {
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
async function fetchMotivation() {
    const display = document.getElementById('motivation-display');
    try {
        const response = await fetch(`${API_URL}/motivation/random`);
        if (response.ok) {
            display.innerText = await response.json();
        } else if (response.status === 404) {
            display.innerText = "No motivation quotes available right now.";
        } else {
            display.innerText = "Couldn't load a quote right now.";
        }
    } catch (err) {
        console.error("Motivation fetch error:", err);
        display.innerText = "Couldn't reach the server.";
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


// =========================================================
// CAREGIVERS: invite links
// =========================================================

function authHeaders(json = false) {
    const h = { 'Authorization': `Bearer ${localStorage.getItem('token')}` };
    if (json) h['Content-Type'] = 'application/json';
    return h;
}

// Build list rows with textContent (never innerHTML) because names/emails are user-supplied.
function addRow(list, mainText, extraText, buttons = []) {
    const li = document.createElement('li');
    const row = document.createElement('div');
    row.className = 'med-item';
    const info = document.createElement('span');
    info.className = 'med-info';
    const strong = document.createElement('strong');
    strong.textContent = mainText;
    info.appendChild(strong);
    if (extraText) info.appendChild(document.createTextNode(' ' + extraText));
    row.appendChild(info);
    if (buttons.length) {
        const actions = document.createElement('div');
        actions.className = 'actions';
        buttons.forEach(b => actions.appendChild(b));
        row.appendChild(actions);
    }
    li.appendChild(row);
    list.appendChild(li);
}

function makeButton(label, cls, onClick) {
    const b = document.createElement('button');
    b.textContent = label;
    b.className = cls;
    b.onclick = onClick;
    return b;
}

function showEmpty(list, text) {
    const li = document.createElement('li');
    li.className = 'empty-note';
    li.textContent = text;
    list.appendChild(li);
}

// --- Patient: create the link ---
async function handleCreateInviteLink() {
    try {
        const response = await fetch(`${API_URL}/caregivers/invite-links`, {
            method: 'POST',
            headers: authHeaders()
        });
        if (response.status === 401) return handleLogout();
        if (!response.ok) {
            alert("Couldn't create the link. Please try again.");
            return;
        }
        const data = await response.json();
        // Token goes in the query string of THIS page, so it works wherever the frontend is hosted.
        const url = `${location.origin}${location.pathname}?invite=${encodeURIComponent(data.token)}`;
        const input = document.getElementById('invite-link-url');
        input.value = url;
        document.getElementById('invite-link-box').hidden = false;
        input.focus();
        input.select();
    } catch (err) {
        console.error("Create invite link error:", err);
        alert("Couldn't reach the server.");
    }
}

async function copyInviteLink() {
    const input = document.getElementById('invite-link-url');
    const btn = document.getElementById('copy-link-btn');
    try {
        await navigator.clipboard.writeText(input.value);
    } catch {
        input.select();           // fallback for non-secure contexts
        document.execCommand('copy');
    }
    btn.textContent = 'Copied!';
    setTimeout(() => { btn.textContent = 'Copy'; }, 1500);
}

// --- Patient: who are my caregivers ---
async function fetchMyCaregivers() {
    const list = document.getElementById('my-caregivers');
    try {
        const response = await fetch(`${API_URL}/caregivers/me`, { headers: authHeaders() });
        if (!response.ok) return;
        const caregivers = await response.json();
        list.innerHTML = '';
        if (!caregivers.length) return showEmpty(list, 'No caregivers yet.');
        caregivers.forEach(c => {
            const label = c.caregiver_name ? `${c.caregiver_name} (${c.caregiver_email})` : c.caregiver_email;
            const status = c.status === 'ACCEPTED' ? 'accepted' : 'waiting for response';
            addRow(list, label, `- ${status}`, [
                makeButton('Remove', 'btn-danger', () => removeCaregiver(c.cg_id))
            ]);
        });
    } catch (err) {
        console.error("Fetch caregivers error:", err);
    }
}

async function removeCaregiver(cgId) {
    if (!confirm("Remove this caregiver? They will no longer see your medications.")) return;
    const response = await fetch(`${API_URL}/caregivers/${cgId}`, {
        method: 'DELETE',
        headers: authHeaders()
    });
    if (response.ok) fetchMyCaregivers();
}

// --- Caregiver: people I look after (read-only) ---
async function fetchMyPatients() {
    const list = document.getElementById('my-patients');
    try {
        const response = await fetch(`${API_URL}/caregivers/me/patients`, { headers: authHeaders() });
        if (!response.ok) return;
        const patients = await response.json();
        list.innerHTML = '';
        if (!patients.length) return showEmpty(list, "You aren't a caregiver for anyone yet.");
        patients.forEach(p => {
            const meds = p.medications.map(m => `${m.name} (${m.dosage})`).join(', ');
            addRow(list, p.patient_email, meds ? `- ${meds}` : '- no active medications');
        });
    } catch (err) {
        console.error("Fetch patients error:", err);
    }
}

// --- Caregiver: open the link, sign in, accept ---
// The link looks like  <frontend>/?invite=TOKEN . Keep the token in sessionStorage so it
// survives sign-in / sign-up, and strip it from the address bar so it isn't left in history.
function captureInviteFromUrl() {
    const token = new URLSearchParams(location.search).get('invite');
    if (token) {
        sessionStorage.setItem('pendingInvite', token);
        history.replaceState(null, '', location.pathname);
    }
}

function setInviteBanner(text, showActions) {
    document.getElementById('invite-text').textContent = text;
    document.getElementById('invite-actions').hidden = !showActions;
    document.getElementById('invite-banner').hidden = false;
}

function clearInviteBanner() {
    sessionStorage.removeItem('pendingInvite');
    document.getElementById('invite-banner').hidden = true;
}

async function loadPendingInvite() {
    const token = sessionStorage.getItem('pendingInvite');
    if (!token) return;
    try {
        const response = await fetch(`${API_URL}/caregivers/invite-links/${encodeURIComponent(token)}`, {
            headers: authHeaders()
        });
        if (response.status === 401) return handleLogout();   // session expired; invite is kept for next sign-in
        const data = await response.json();
        if (response.ok) {
            const who = data.patient_name ? `${data.patient_name} (${data.patient_email})` : data.patient_email;
            setInviteBanner(`${who} would like you to be their caregiver. If you accept, you will be able to see their active medications (read-only).`, true);
        } else {
            sessionStorage.removeItem('pendingInvite');
            setInviteBanner(formatError(data, "This invite link isn't valid."), false);
            setTimeout(clearInviteBanner, 8000);
        }
    } catch (err) {
        console.error("Invite preview error:", err);
    }
}

async function acceptInvite() {
    const token = sessionStorage.getItem('pendingInvite');
    if (!token) return;
    try {
        const response = await fetch(`${API_URL}/caregivers/invite-links/${encodeURIComponent(token)}/accept`, {
            method: 'POST',
            headers: authHeaders()
        });
        if (response.status === 401) return handleLogout();
        if (response.ok) {
            clearInviteBanner();
            fetchMyPatients();
            alert("You're now a caregiver. Their medications appear under 'People I care for'.");
        } else {
            const data = await response.json();
            sessionStorage.removeItem('pendingInvite');
            setInviteBanner(formatError(data, "Couldn't accept the invitation."), false);
        }
    } catch (err) {
        console.error("Accept invite error:", err);
    }
}

function declineInvite() {
    clearInviteBanner();   // nothing was granted, so declining just discards the link
}
