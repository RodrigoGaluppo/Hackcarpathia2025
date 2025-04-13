const scoreCircle = document.getElementById('score-circle');
const resultLabel = document.getElementById('result-label');

function createVendorRow(engine, verdict, details) {
  const row = document.createElement('tr');
  row.innerHTML = `
    <td>${engine}</td>
    <td><span class="badge ${verdict === 'Malicious' ? 'badge-danger' : 'badge-success'}">${verdict}</span></td>
    <td>${typeof details === 'string' ? details : details.result || 'Detected as malicious'}</td>
  `;
  return row;
}

function renderLinkSection(linkData) {
  const container = document.createElement('div');
  container.classList.add('mt-5');

  const table = document.createElement('table');
  table.className = 'table table-bordered table-striped mt-3';

  const thead = document.createElement('thead');
  thead.innerHTML = `
    <tr>
      <th>Engine</th>
      <th>Verdict</th>
      <th>Classification</th>
    </tr>
  `;

  const tbody = document.createElement('tbody');

  const report = linkData.report || {};
  const maliciousReports = report.malicious_reports || {};
  const hasVendors = Object.keys(maliciousReports).length > 0;

  if (hasVendors) {
    for (const [vendor, reason] of Object.entries(maliciousReports)) {
      tbody.appendChild(createVendorRow(vendor, 'Malicious', reason));
    }
  } else {
    tbody.appendChild(createVendorRow('All Vendors', 'Clean', 'No malicious activity detected.'));
  }

  table.appendChild(thead);
  table.appendChild(tbody);

  const title = document.createElement('h4');
  title.className = 'text-info';
  title.textContent = `Link: ${linkData.link}`;

  container.appendChild(title);
  container.appendChild(table);
  document.body.appendChild(container);
}

chrome.storage.local.get(['analysis'], (result) => {
  const analysis = result.analysis;
  if (!analysis) return;

  const score = analysis.score || 0;
  const labelText = analysis.label || 'Unknown';

  // Set the score
  scoreCircle.textContent = `${score}%`;

  // Set label and styling based on actual label
  if (labelText.toLowerCase() === 'malicious') {
    scoreCircle.classList.remove('good');
    scoreCircle.classList.add('bad');
    resultLabel.textContent = 'Malicious';
    resultLabel.classList.add('text-danger');
  } else {
    scoreCircle.classList.remove('bad');
    scoreCircle.classList.add('good');
    resultLabel.textContent = labelText;
    resultLabel.classList.remove('text-danger');
  }

  // Render reports per link if any
  if (Array.isArray(analysis.links)) {
    analysis.links.forEach(renderLinkSection);
  }
});
