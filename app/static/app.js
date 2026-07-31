document.addEventListener("DOMContentLoaded", () => {
    const workpiecesBody = document.getElementById("workpiecesBody");
    const addRowBtn = document.getElementById("addRowBtn");
    const loadExampleBtn = document.getElementById("loadExampleBtn");
    const clearBtn = document.getElementById("clearBtn");
    const calculateBtn = document.getElementById("calculateBtn");
    const maxLengthInput = document.getElementById("maxLength");
    const btnText = document.getElementById("btnText");
    const btnSpinner = document.getElementById("btnSpinner");
    const errorMessage = document.getElementById("errorMessage");
    const resultsSection = document.getElementById("resultsSection");

    // Начальные примерные данные
    const exampleData = [
        { length: 6360, quantity: 10 },
        { length: 5070, quantity: 12 },
        { length: 2070, quantity: 15 },
        { length: 1650, quantity: 20 }
    ];

    function createRow(length = "", quantity = "") {
        const tr = document.createElement("tr");
        const rowCount = workpiecesBody.children.length + 1;

        tr.innerHTML = `
            <td class="row-index">${rowCount}</td>
            <td>
                <input type="number" class="wp-length" placeholder="Например, 3500" min="1" step="1" value="${length}" required>
            </td>
            <td>
                <input type="number" class="wp-quantity" placeholder="Например, 10" min="1" step="1" value="${quantity}" required>
            </td>
            <td>
                <button type="button" class="btn-icon delete-row-btn" title="Удалить позицию">❌</button>
            </td>
        `;

        tr.querySelector(".delete-row-btn").addEventListener("click", () => {
            tr.remove();
            updateRowIndices();
        });

        workpiecesBody.appendChild(tr);
    }

    function updateRowIndices() {
        const rows = workpiecesBody.querySelectorAll("tr");
        rows.forEach((row, index) => {
            row.querySelector(".row-index").textContent = index + 1;
        });
    }

    function clearTable() {
        workpiecesBody.innerHTML = "";
        hideError();
        resultsSection.classList.add("hidden");
    }

    function loadExample() {
        clearTable();
        exampleData.forEach(item => createRow(item.length, item.quantity));
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        errorMessage.classList.remove("hidden");
    }

    function hideError() {
        errorMessage.textContent = "";
        errorMessage.classList.add("hidden");
    }

    function setLoading(isLoading) {
        if (isLoading) {
            btnText.textContent = "Расчёт...";
            btnSpinner.classList.remove("hidden");
            calculateBtn.disabled = true;
        } else {
            btnText.textContent = "Рассчитать раскрой";
            btnSpinner.classList.add("hidden");
            calculateBtn.disabled = false;
        }
    }

    // Инициализация полей ввода по умолчанию
    loadExample();

    addRowBtn.addEventListener("click", () => createRow());
    loadExampleBtn.addEventListener("click", loadExample);
    clearBtn.addEventListener("click", clearTable);

    calculateBtn.addEventListener("click", async () => {
        hideError();
        
        const maxLength = parseInt(maxLengthInput.value, 10);
        if (!maxLength || maxLength <= 0) {
            showError("Укажите корректную длину хлыста (> 0).");
            return;
        }

        const rows = workpiecesBody.querySelectorAll("tr");
        if (rows.length === 0) {
            showError("Добавьте хотя бы одну заготовку.");
            return;
        }

        const workpieces = [];
        const requestedDemands = {}; // length -> total requested quantity
        let hasInvalidInput = false;

        rows.forEach((row, idx) => {
            const lengthVal = parseInt(row.querySelector(".wp-length").value, 10);
            const quantityVal = parseInt(row.querySelector(".wp-quantity").value, 10);

            if (!lengthVal || lengthVal <= 0 || !quantityVal || quantityVal <= 0) {
                hasInvalidInput = true;
                return;
            }

            if (lengthVal > maxLength) {
                showError(`Строка ${idx + 1}: длина заготовки (${lengthVal} мм) превышает длину хлыста (${maxLength} мм).`);
                hasInvalidInput = true;
                return;
            }

            workpieces.push({
                length: lengthVal,
                quantity: quantityVal
            });

            requestedDemands[lengthVal] = (requestedDemands[lengthVal] || 0) + quantityVal;
        });

        if (hasInvalidInput) {
            if (!errorMessage.textContent) {
                showError("Пожалуйста, заполните все поля корректными положительными числами.");
            }
            return;
        }

        const payload = {
            input: {
                workpieces: workpieces
            },
            max_length: maxLength
        };

        setLoading(true);

        try {
            const response = await fetch("/gilgom", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errText = await response.text();
                throw new Error(`Ошибка сервера: ${response.status} ${errText}`);
            }

            const data = await response.json();
            renderResults(data, maxLength, requestedDemands);

        } catch (err) {
            console.error(err);
            showError(err.message || "Произошла ошибка при выполнении расчёта.");
        } finally {
            setLoading(false);
        }
    });

    function renderResults(data, maxLength, requestedDemands) {
        const patterns = data.patterns || [];
        const totalWhips = data.total_whips || 0;

        // Расчёт совокупной статистики
        let totalUsedMm = 0;
        let totalWasteMm = 0;
        const totalStockMm = totalWhips * maxLength;

        patterns.forEach(p => {
            const count = p.count || 0;
            const cutBar = p.cutted_bar || {};
            totalUsedMm += (cutBar.used_length || 0) * count;
            totalWasteMm += (cutBar.left_length || 0) * count;
        });

        const usedMeters = (totalUsedMm / 1000).toFixed(2);
        const wasteMeters = (totalWasteMm / 1000).toFixed(2);
        const totalStockMeters = (totalStockMm / 1000).toFixed(2);

        const usedPercent = totalStockMm > 0 ? ((totalUsedMm / totalStockMm) * 100).toFixed(1) : 0;
        const wastePercent = totalStockMm > 0 ? ((totalWasteMm / totalStockMm) * 100).toFixed(1) : 0;

        document.getElementById("statTotalWhips").textContent = `${totalWhips} шт`;
        document.getElementById("statTotalStockMeters").textContent = `(${totalStockMeters} м)`;

        document.getElementById("statUsedLength").textContent = `${usedMeters} м`;
        document.getElementById("statUsedPercent").textContent = `${usedPercent}% от закупки`;

        document.getElementById("statWasteLength").textContent = `${wasteMeters} м`;
        document.getElementById("statWastePercent").textContent = `${wastePercent}% от закупки`;

        // Рендеринг таблицы шаблонов
        const patternsTableBody = document.getElementById("patternsTableBody");
        patternsTableBody.innerHTML = "";

        const cuttedCountsByLength = {};

        patterns.forEach((p, idx) => {
            const count = p.count;
            const bar = p.cutted_bar;

            // Группировка заготовок в шаблоне по длине
            const groupedInPattern = {};
            (bar.workpieces || []).forEach(wp => {
                groupedInPattern[wp.length] = (groupedInPattern[wp.length] || 0) + 1;

                // Учёт общей раскроенной партии
                cuttedCountsByLength[wp.length] = (cuttedCountsByLength[wp.length] || 0) + count;
            });

            const compositionStr = Object.entries(groupedInPattern)
                .map(([len, qty]) => `<b>${len} мм</b> × ${qty} шт`)
                .join(", ");

            const kin = ((bar.used_length / maxLength) * 100).toFixed(1);

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><b>№ ${idx + 1}</b></td>
                <td><b>${count}</b> шт</td>
                <td>${compositionStr}</td>
                <td>${bar.used_length} мм (${(bar.used_length / 1000).toFixed(2)} м)</td>
                <td>${bar.left_length} мм (${(bar.left_length / 1000).toFixed(2)} м)</td>
                <td><span class="badge-success">${kin}%</span></td>
            `;
            patternsTableBody.appendChild(tr);
        });

        // Рендеринг сводки заказа vs полученного расчёта
        const summaryTableBody = document.getElementById("summaryTableBody");
        summaryTableBody.innerHTML = "";

        Object.entries(requestedDemands).forEach(([lenStr, reqQty]) => {
            const len = parseInt(lenStr, 10);
            const actualQty = cuttedCountsByLength[len] || 0;
            const isOk = actualQty >= reqQty;

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><b>${len} мм</b></td>
                <td>${reqQty} шт</td>
                <td>${actualQty} шт</td>
                <td>${isOk ? '✅ Выполнено' : '⚠️ Недобор'}</td>
            `;
            summaryTableBody.appendChild(tr);
        });

        resultsSection.classList.remove("hidden");
        resultsSection.scrollIntoView({ behavior: "smooth" });
    }
});
