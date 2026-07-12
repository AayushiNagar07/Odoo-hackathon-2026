document.addEventListener('DOMContentLoaded', () => {
    const fuelBody = document.getElementById('fuelLogsBody');
    const expensesBody = document.getElementById('expensesBody');
    const fuelSummary = document.getElementById('fuelSummary');
    const expenseSummary = document.getElementById('expenseSummary');
    const grandTotal = document.getElementById('grandTotal');

    const fuelModalEl = document.getElementById('fuelModal');
    const expenseModalEl = document.getElementById('expenseModal');
    const fuelForm = document.getElementById('fuelForm');
    const expenseForm = document.getElementById('expenseForm');
    const addFuelLogBtn = document.getElementById('addFuelLogBtn');
    const addExpenseBtn = document.getElementById('addExpenseBtn');

    const fuelModal = new bootstrap.Modal(fuelModalEl);
    const expenseModal = new bootstrap.Modal(expenseModalEl);
    let latestFuelLogs = [];
    let latestExpenses = [];

    addFuelLogBtn?.addEventListener('click', () => fuelModal.show());
    addExpenseBtn?.addEventListener('click', () => expenseModal.show());

    fuelForm?.addEventListener('submit', async (event) => {
        event.preventDefault();
        const payload = Object.fromEntries(new FormData(fuelForm).entries());
        payload.liters = Number(payload.liters || 0);
        payload.cost = Number(payload.cost || 0);

        const response = await fetch('/api/fuel_logs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            alert(data.message || 'Unable to add fuel log.');
            return;
        }

        fuelForm.reset();
        fuelModal.hide();
        await loadData();
    });

    expenseForm?.addEventListener('submit', async (event) => {
        event.preventDefault();
        const payload = Object.fromEntries(new FormData(expenseForm).entries());
        payload.toll = Number(payload.toll || 0);
        payload.other = Number(payload.other || 0);

        const response = await fetch('/api/expenses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            alert(data.message || 'Unable to add expense.');
            return;
        }

        expenseForm.reset();
        expenseModal.hide();
        await loadData();
    });

    async function loadData() {
        const [fuelResponse, expenseResponse] = await Promise.all([
            fetch('/api/fuel_logs'),
            fetch('/api/expenses')
        ]);

        latestFuelLogs = await fuelResponse.json();
        latestExpenses = await expenseResponse.json();

        renderFuelLogs(latestFuelLogs);
        renderExpenses(latestExpenses);
    }

    function renderFuelLogs(rows) {
        if (!rows.length) {
            fuelBody.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-4">No fuel logs yet.</td></tr>';
            fuelSummary.innerHTML = '<span class="text-muted">No data</span>';
            updateGrandTotal();
            return;
        }

        const totalLiters = rows.reduce((sum, row) => sum + Number(row.liters || 0), 0);
        const totalCost = rows.reduce((sum, row) => sum + Number(row.cost || 0), 0);

        fuelBody.innerHTML = rows.map((row) => `
            <tr>
                <td>${row.vehicle}</td>
                <td>${row.date}</td>
                <td>${Number(row.liters).toFixed(2)} L</td>
                <td class="fw-bold">${formatCurrency(row.cost)}</td>
            </tr>
        `).join('');

        fuelSummary.innerHTML = `
            <span class="me-3">Liters: <strong>${totalLiters.toFixed(2)} L</strong></span>
            <span>Cost: <strong>${formatCurrency(totalCost)}</strong></span>
        `;

        updateGrandTotal(totalCost, getExpenseTotal(latestExpenses));
    }

    function renderExpenses(rows) {
        if (!rows.length) {
            expensesBody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4">No expenses yet.</td></tr>';
            expenseSummary.innerHTML = '<span class="text-muted">No data</span>';
            updateGrandTotal();
            return;
        }

        const totalExpenses = rows.reduce((sum, row) => sum + Number(row.toll || 0) + Number(row.other || 0), 0);

        expensesBody.innerHTML = rows.map((row) => `
            <tr>
                <td>${row.expense_type}</td>
                <td>${row.vehicle}</td>
                <td>${formatCurrency(row.toll || 0)}</td>
                <td>${formatCurrency(row.other || 0)}</td>
                <td class="fw-bold">${formatCurrency((Number(row.toll || 0) + Number(row.other || 0)))}</td>
            </tr>
        `).join('');

        expenseSummary.innerHTML = `<span class="fw-semibold">${formatCurrency(totalExpenses)}</span>`;
        updateGrandTotal(getFuelTotal(latestFuelLogs), totalExpenses);
    }

    function getExpenseTotal(rows) {
        return rows.reduce((sum, row) => sum + Number(row.toll || 0) + Number(row.other || 0), 0);
    }

    function getFuelTotal(rows) {
        return rows.reduce((sum, row) => sum + Number(row.cost || 0), 0);
    }

    function updateGrandTotal(fuelCost = 0, expenseCost = 0) {
        grandTotal.textContent = formatCurrency(Number(fuelCost || 0) + Number(expenseCost || 0));
    }

    function formatCurrency(value) {
        return `₹ ${Number(value || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
    }

    loadData();
});
