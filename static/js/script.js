/* ═══════════════════════════════════════════════════════════════════════════
   CPSMS – Client-side JavaScript
   Handles tabs, modals, AJAX slot loading, and live updates
   ═══════════════════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    autoCloseFlash();
});

// ── Tab Switching ───────────────────────────────────────────────────────────
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;

            // Deactivate all
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));

            // Activate selected
            btn.classList.add('active');
            const panel = document.getElementById(`panel-${tabName}`);
            if (panel) panel.classList.add('active');
        });
    });
}

// ── Modal Open / Close ──────────────────────────────────────────────────────
function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.style.display = 'flex';
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.style.display = 'none';
}

// Close modal on overlay click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.style.display = 'none';
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay').forEach(m => m.style.display = 'none');
    }
});

// ── Load Parking Slots (AJAX) ───────────────────────────────────────────────
function loadSlots() {
    const grid = document.getElementById('slotGrid');
    if (!grid) return;

    const filterInput = document.getElementById('slotFilter');
    const location = filterInput ? filterInput.value.trim() : '';

    grid.innerHTML = '<div class="loading-spinner">Loading slots...</div>';

    fetch(`/user/api/slots?location=${encodeURIComponent(location)}`)
        .then(res => res.json())
        .then(slots => {
            if (slots.length === 0) {
                grid.innerHTML = '<div class="empty-state">No parking slots available.</div>';
                return;
            }

            grid.innerHTML = '';
            slots.forEach(slot => {
                const isAvailable = slot.slot_status === 'Available';
                const card = document.createElement('div');
                card.className = `slot-card ${isAvailable ? 'available' : 'occupied'}`;
                card.innerHTML = `
                    <div class="slot-id">#${slot.slot_id}</div>
                    <div class="slot-loc">${escapeHtml(slot.slot_location)}</div>
                    <div>
                        <span class="slot-status-dot ${isAvailable ? 'green' : 'red'}"></span>
                        <span class="slot-status-text ${isAvailable ? 'available' : 'occupied'}">${slot.slot_status}</span>
                    </div>
                `;

                if (isAvailable) {
                    card.addEventListener('click', () => openReserveModal(slot));
                }

                grid.appendChild(card);
            });
        })
        .catch(() => {
            grid.innerHTML = '<div class="empty-state">Failed to load slots. Please try again.</div>';
        });
}

function openReserveModal(slot) {
    const modal = document.getElementById('reserveModal');
    if (!modal) return;

    document.getElementById('reserveSlotId').value = slot.slot_id;
    document.getElementById('reserveSlotInfo').textContent = `Slot #${slot.slot_id} – ${slot.slot_location}`;
    modal.style.display = 'flex';
}

// ── Edit Vehicle ────────────────────────────────────────────────────────────
function openEditVehicle(vehicleId, number, type) {
    document.getElementById('editVehicleForm').action = `/user/vehicle/edit/${vehicleId}`;
    document.getElementById('editVehicleNumber').value = number;
    document.getElementById('editVehicleType').value = type;
    openModal('editVehicleModal');
}

// ── Auto-close Flash Messages ───────────────────────────────────────────────
function autoCloseFlash() {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            flash.style.opacity = '0';
            flash.style.transform = 'translateY(-10px)';
            setTimeout(() => flash.remove(), 400);
        }, 5000);
    });
}

// ── Live Slot Refresh (auto every 15 seconds) ───────────────────────────────
(function autoRefreshSlots() {
    setInterval(() => {
        const slotsPanel = document.getElementById('panel-slots');
        if (slotsPanel && slotsPanel.classList.contains('active')) {
            loadSlots();
        }
    }, 15000);
})();

// ── Filter Slots on Input ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const filterInput = document.getElementById('slotFilter');
    if (filterInput) {
        let debounceTimer;
        filterInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(loadSlots, 400);
        });
    }
});

// ── Escape HTML ─────────────────────────────────────────────────────────────
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
