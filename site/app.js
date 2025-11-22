const SUMMARY_CARD_CONFIG = [
    { key: "52WH(%)", label: "52W High %" },
    { key: "52WL(%)", label: "52W Low %" },
    { key: "4.5+(%)", label: "4.5% Advancers" },
    { key: "4.5-(%)", label: "4.5% Decliners" },
    { key: "4.5r", label: "4.5 Ratio" },
];

const statusBox = document.getElementById("status");
const summaryBox = document.getElementById("summary");
const tableHead = document.getElementById("tableHead");
const tableBody = document.getElementById("tableBody");

init();

async function init() {
    try {
        statusBox.textContent = "Loading latest breadth data…";
        const csvText = await fetchCsv("market_breadth.csv");
        const { header, rows } = parseCsv(csvText);
        if (!rows.length) {
            statusBox.textContent = "No breadth data available yet.";
            return;
        }

        const last60 = rows.slice(-60);
        renderSummary(header, last60);
        renderTable(header, last60);

        const latestDate = last60.at(-1)?.Date ?? "";
        statusBox.textContent = `Showing ${last60.length} of ${rows.length} total records · Updated ${formatDate(latestDate)}`;
    } catch (error) {
        console.error(error);
        statusBox.innerHTML = `⚠️ Unable to load data. <code>${error.message}</code>`;
    }
}

async function fetchCsv(path) {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
    }
    return response.text();
}

function parseCsv(text) {
    const lines = text.trim().split(/\r?\n/).filter(Boolean);
    const header = lines.shift().split(",").map((cell) => cell.trim());
    const rows = lines.map((line) => {
        const values = line.split(",");
        return header.reduce((acc, key, idx) => {
            acc[key] = values[idx]?.trim() ?? "";
            return acc;
        }, {});
    });
    return { header, rows };
}

function renderSummary(header, rows) {
    if (!rows.length) {
        summaryBox.innerHTML = "";
        return;
    }

    const latest = rows.at(-1);
    const cards = [
        summaryCard("Last Update", formatDate(latest.Date)),
        ...SUMMARY_CARD_CONFIG.map(({ key, label }) => summaryCard(label, formatNumber(latest[key]))),
    ];

    summaryBox.innerHTML = cards.join("");
}

function renderTable(header, rows) {
    tableHead.innerHTML = `<tr>${header.map((col) => `<th>${col}</th>`).join("")}</tr>`;
    tableBody.innerHTML = rows
        .map((row) => `<tr>${header.map((col) => `<td>${formatCell(col, row[col])}</td>`).join("")}</tr>`)
        .join("");
}

function formatCell(column, value) {
    if (column === "Date") {
        return formatDate(value);
    }
    if (value === undefined || value === "") {
        return "—";
    }
    return formatNumber(value);
}

function formatNumber(value) {
    const num = Number(value);
    if (Number.isNaN(num)) {
        return value ?? "—";
    }
    return num % 1 === 0 ? num.toString() : num.toFixed(2);
}

function formatDate(value) {
    if (!value) return "—";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleDateString("en-IN", { year: "numeric", month: "short", day: "numeric" });
}

function summaryCard(label, value) {
    return `
        <article class="summary-card">
            <h3>${label}</h3>
            <p>${value}</p>
        </article>
    `;
}
