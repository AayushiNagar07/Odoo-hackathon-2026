document.addEventListener("DOMContentLoaded", () => {
    const driversTableBody = document.getElementById('driversTableBody');
    const driverSearch = document.getElementById('driverSearch');
    const statusButtons = Array.from(document.querySelectorAll('.status-filter-group .btn-status'));
    const addDriverBtn = document.getElementById('addDriverBtn');
    const addDriverModalEl = document.getElementById('addDriverModal');
    const addDriverForm = document.getElementById('addDriverForm');
    const pageFeedback = document.getElementById('pageFeedback');
    const formFeedback = document.getElementById('formFeedback');

    if (!driversTableBody || !driverSearch || !addDriverForm) {
        return;
    }

    const addDriverModal = addDriverModalEl ? new bootstrap.Modal(addDriverModalEl) : null;
    let currentStatusFilter = 'all';
    let currentSearch = '';

    async function loadDrivers() {
        const query = new URLSearchParams();
        if (currentSearch) query.set('search', currentSearch);
        if (currentStatusFilter !== 'all') query.set('status', currentStatusFilter);

        try {
            const response = await fetch(`/api/drivers?${query.toString()}`);
            if (!response.ok) {
                driversTableBody.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-5">Unable to load drivers.</td></tr>';
                return;
            }

            const drivers = await response.json();
            renderDrivers(drivers);
        } catch (error) {
            driversTableBody.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-5">Unable to load drivers.</td></tr>';
        }
    }

    function renderDrivers(drivers) {
        if (!drivers.length) {
            driversTableBody.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-5">No drivers found.</td></tr>';
            return;
        }

        driversTableBody.innerHTML = drivers.map(driver => {
            return `
                <tr>
                    <td>${driver.driver_name || '-'}</td>
                    <td>${driver.license_no || '-'}</td>
                    <td>${driver.category || '-'}</td>
                    <td>${formatExpiry(driver.expiry)}</td>
                    <td>${driver.contact || '-'}</td>
                    <td>${driver.trip_completion || '-'}</td>
                    <td><span class="safety-pill ${getPillClass(driver.safety_status)}">${driver.safety_status || 'Available'}</span></td>
                    <td><span class="status-pill ${getPillClass(driver.status)}">${formatStatusLabel(driver.status)}</span></td>
                </tr>
            `;
        }).join('');
    }

    function getPillClass(value) {
        const normalized = normalizeStatus(value);
        return ['available', 'on_trip', 'off_duty', 'suspended'].includes(normalized) ? normalized : 'off_duty';
    }

    function normalizeStatus(value) {
        if (!value) return 'off_duty';
        return value.toString().trim().toLowerCase().replace(/\s+/g, '_');
    }

    function formatStatusLabel(value) {
        if (!value) return 'Off Duty';
        return value.toString().trim().replace(/_/g, ' ').replace(/\b\w/g, letter => letter.toUpperCase());
    }

    function formatExpiry(value) {
        if (!value) return '-';
        const parts = value.split('-');
        if (parts.length === 2) {
            return `${parts[1]}/${parts[0]}`;
        }
        return value;
    }

    function updateActiveFilterButton() {
        statusButtons.forEach(button => {
            button.classList.toggle('active', button.dataset.status === currentStatusFilter);
        });
    }

    function showFeedback(message, isError = false, target = pageFeedback) {
        if (!target) return;
        target.className = `alert ${isError ? 'alert-danger' : 'alert-success'} mb-3`;
        target.textContent = message;
        target.classList.remove('d-none');
        clearTimeout(showFeedback.timer);
        showFeedback.timer = setTimeout(() => target.classList.add('d-none'), 2400);
    }

    driverSearch.addEventListener('input', debounce((event) => {
        currentSearch = event.target.value.trim();
        loadDrivers();
    }, 220));

    statusButtons.forEach(button => {
        button.addEventListener('click', () => {
            currentStatusFilter = button.dataset.status;
            updateActiveFilterButton();
            loadDrivers();
        });
    });

    addDriverBtn?.addEventListener('click', () => {
        if (formFeedback) {
            formFeedback.classList.add('d-none');
            formFeedback.textContent = '';
        }
        addDriverModal?.show();
    });

    addDriverForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(addDriverForm);
        const payload = Object.fromEntries(formData.entries());
        payload.status = (payload.status || 'available').trim().toLowerCase();

        if (!payload.driver_name || !payload.license_no) {
            if (formFeedback) {
                formFeedback.className = 'alert alert-danger mb-3';
                formFeedback.textContent = 'Driver name and license number are required.';
                formFeedback.classList.remove('d-none');
            }
            return;
        }

        try {
            const response = await fetch('/api/drivers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                if (formFeedback) {
                    formFeedback.className = 'alert alert-danger mb-3';
                    formFeedback.textContent = data.message || 'Unable to add driver.';
                    formFeedback.classList.remove('d-none');
                }
                return;
            }

            addDriverForm.reset();
            addDriverModal?.hide();
            showFeedback(data.message || 'Driver added successfully.');
            loadDrivers();
        } catch (error) {
            if (formFeedback) {
                formFeedback.className = 'alert alert-danger mb-3';
                formFeedback.textContent = 'Unable to add driver right now.';
                formFeedback.classList.remove('d-none');
            }
        }
    });

    function debounce(fn, delay) {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn(...args), delay);
        };
    }

    updateActiveFilterButton();
    loadDrivers();
});
