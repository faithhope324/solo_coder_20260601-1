document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    initSingleUpload();
    initBatchUpload();
    initEvaluateButtons();
    initDetailsToggle();
});

function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;

            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(tabId + '-tab').classList.add('active');
        });
    });
}

function initSingleUpload() {
    setupFileDrop(
        'standard-drop',
        'standard-input',
        'standard-preview',
        validateSingleForm
    );

    setupFileDrop(
        'practice-drop',
        'practice-input',
        'practice-preview',
        validateSingleForm
    );

    document.getElementById('reset-btn').addEventListener('click', resetSingleForm);
}

function initBatchUpload() {
    setupFileDrop(
        'batch-standard-drop',
        'batch-standard-input',
        'batch-standard-preview',
        validateBatchForm
    );

    setupZipDrop(
        'batch-zip-drop',
        'batch-zip-input',
        'batch-zip-info',
        validateBatchForm
    );

    document.getElementById('batch-reset-btn').addEventListener('click', resetBatchForm);
}

function setupFileDrop(dropId, inputId, previewId, validateCallback) {
    const dropZone = document.getElementById(dropId);
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    const placeholder = dropZone.querySelector('.drop-placeholder');

    dropZone.addEventListener('click', () => input.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleImageFile(files[0], preview, placeholder, validateCallback);
        }
    });

    input.addEventListener('change', () => {
        if (input.files.length > 0) {
            handleImageFile(input.files[0], preview, placeholder, validateCallback);
        }
    });
}

function setupZipDrop(dropId, inputId, infoId, validateCallback) {
    const dropZone = document.getElementById(dropId);
    const input = document.getElementById(inputId);
    const info = document.getElementById(infoId);
    const placeholder = dropZone.querySelector('.drop-placeholder');

    dropZone.addEventListener('click', () => input.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleZipFile(files[0], info, placeholder, validateCallback);
        }
    });

    input.addEventListener('change', () => {
        if (input.files.length > 0) {
            handleZipFile(input.files[0], info, placeholder, validateCallback);
        }
    });
}

function handleImageFile(file, preview, placeholder, validateCallback) {
    if (!file.type.startsWith('image/')) {
        showError('请上传图片文件');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        preview.src = e.target.result;
        preview.style.display = 'block';
        placeholder.style.display = 'none';
        if (validateCallback) validateCallback();
    };
    reader.readAsDataURL(file);
}

function handleZipFile(file, info, placeholder, validateCallback) {
    if (!file.name.toLowerCase().endsWith('.zip')) {
        showError('请上传 ZIP 格式压缩包');
        return;
    }

    info.innerHTML = `
        <div class="icon">📦</div>
        <p><strong>${file.name}</strong></p>
        <span class="hint">${formatFileSize(file.size)}</span>
    `;
    info.style.display = 'block';
    placeholder.style.display = 'none';
    if (validateCallback) validateCallback();
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function validateSingleForm() {
    const standard = document.getElementById('standard-preview').style.display === 'block';
    const practice = document.getElementById('practice-preview').style.display === 'block';
    document.getElementById('evaluate-btn').disabled = !(standard && practice);
}

function validateBatchForm() {
    const standard = document.getElementById('batch-standard-preview').style.display === 'block';
    const zipInfo = document.getElementById('batch-zip-info').style.display === 'block';
    document.getElementById('batch-evaluate-btn').disabled = !(standard && zipInfo);
}

function resetSingleForm() {
    document.getElementById('standard-input').value = '';
    document.getElementById('practice-input').value = '';
    document.getElementById('standard-preview').src = '';
    document.getElementById('practice-preview').src = '';
    document.getElementById('standard-preview').style.display = 'none';
    document.getElementById('practice-preview').style.display = 'none';
    document.querySelectorAll('#single-tab .drop-placeholder').forEach(p => p.style.display = 'block');
    document.getElementById('evaluate-btn').disabled = true;
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('error-message').style.display = 'none';
}

function resetBatchForm() {
    document.getElementById('batch-standard-input').value = '';
    document.getElementById('batch-zip-input').value = '';
    document.getElementById('batch-standard-preview').src = '';
    document.getElementById('batch-standard-preview').style.display = 'none';
    document.getElementById('batch-zip-info').innerHTML = '';
    document.getElementById('batch-zip-info').style.display = 'none';
    document.querySelectorAll('#batch-tab .drop-placeholder').forEach(p => p.style.display = 'block');
    document.getElementById('batch-evaluate-btn').disabled = true;
    document.getElementById('batch-results-section').style.display = 'none';
    document.getElementById('error-message').style.display = 'none';
}

function initEvaluateButtons() {
    document.getElementById('evaluate-btn').addEventListener('click', evaluateSingle);
    document.getElementById('batch-evaluate-btn').addEventListener('click', evaluateBatch);
}

function evaluateSingle() {
    const standardInput = document.getElementById('standard-input');
    const practiceInput = document.getElementById('practice-input');

    if (standardInput.files.length === 0 || practiceInput.files.length === 0) {
        showError('请上传两张图片');
        return;
    }

    const btn = document.getElementById('evaluate-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');

    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';

    hideError();

    const formData = new FormData();
    formData.append('standard', standardInput.files[0]);
    formData.append('practice', practiceInput.files[0]);

    fetch('/api/evaluate', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';

        if (data.success) {
            displayResults(data);
        } else {
            showError(data.error || '评估失败');
        }
    })
    .catch(error => {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        showError('请求失败: ' + error.message);
    });
}

function evaluateBatch() {
    const standardInput = document.getElementById('batch-standard-input');
    const zipInput = document.getElementById('batch-zip-input');

    if (standardInput.files.length === 0 || zipInput.files.length === 0) {
        showError('请上传标准姿势图和 ZIP 压缩包');
        return;
    }

    const btn = document.getElementById('batch-evaluate-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');

    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';

    hideError();

    const formData = new FormData();
    formData.append('standard', standardInput.files[0]);
    formData.append('practice_zip', zipInput.files[0]);

    fetch('/api/batch-evaluate', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';

        if (data.success) {
            displayBatchResults(data);
        } else {
            showError(data.error || '批量评估失败');
        }
    })
    .catch(error => {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        showError('请求失败: ' + error.message);
    });
}

function displayResults(data) {
    const resultsSection = document.getElementById('results-section');
    resultsSection.style.display = 'block';

    const scoreNumber = document.getElementById('score-number');
    scoreNumber.textContent = data.score;
    scoreNumber.style.color = data.score_color;

    const scoreFill = document.getElementById('score-fill');
    setTimeout(() => {
        scoreFill.style.width = data.score + '%';
    }, 100);

    document.getElementById('result-standard-orig').src = data.standard_image;
    document.getElementById('result-practice-orig').src = data.practice_image;
    document.getElementById('result-standard-pose').src = data.standard_pose_image;
    document.getElementById('result-practice-pose').src = data.practice_pose_image;

    document.getElementById('suggestion-summary').textContent = data.summary;

    const suggestionsList = document.getElementById('suggestions-list');
    suggestionsList.innerHTML = '';

    if (data.suggestions && data.suggestions.length > 0) {
        data.suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'suggestion-item ' + suggestion.severity;

            let icon = '✓';
            if (suggestion.severity === 'high') icon = '⚠️';
            else if (suggestion.severity === 'medium') icon = '💡';

            item.innerHTML = `
                <div class="suggestion-icon">${icon}</div>
                <div class="suggestion-content">
                    <div class="suggestion-text">${suggestion.suggestion}</div>
                    <div class="suggestion-detail">
                        ${suggestion.angle_name}：标准 ${suggestion.standard_angle}°，练习 ${suggestion.practice_angle}°，差异 ${suggestion.difference}°
                    </div>
                </div>
            `;
            suggestionsList.appendChild(item);
        });
    } else {
        suggestionsList.innerHTML = '<div class="suggestion-item"><div class="suggestion-icon">🎉</div><div class="suggestion-content"><div class="suggestion-text">动作非常标准，没有需要特别改进的地方！</div></div></div>';
    }

    populateAngleTable(data.angle_differences);

    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displayBatchResults(data) {
    const resultsSection = document.getElementById('batch-results-section');
    resultsSection.style.display = 'block';

    document.getElementById('batch-total').textContent = data.total_count;
    document.getElementById('batch-success').textContent = data.success_count;
    document.getElementById('batch-avg').textContent = data.avg_score;

    const downloadBtn = document.getElementById('download-csv-btn');
    downloadBtn.href = data.csv_download_url;

    const grid = document.getElementById('batch-results-grid');
    grid.innerHTML = '';

    data.results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'batch-result-item';

        if (result.success) {
            item.innerHTML = `
                <img src="${result.annotated_image}" alt="${result.filename}">
                <div class="batch-result-info">
                    <div class="batch-result-name">${result.filename}</div>
                    <div class="batch-result-score">
                        <span class="batch-score-value" style="color: ${getScoreColor(result.score)}">${result.score}</span>
                        <span style="color: #888; font-size: 0.85rem;">分</span>
                    </div>
                </div>
            `;
        } else {
            item.classList.add('error');
            item.innerHTML = `
                <div style="padding: 40px; text-align: center;">
                    <div style="font-size: 3rem;">❌</div>
                </div>
                <div class="batch-result-info">
                    <div class="batch-result-name">${result.filename}</div>
                    <div style="color: #ef4444; font-size: 0.85rem;">${result.error}</div>
                </div>
            `;
        }

        grid.appendChild(item);
    });

    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function getScoreColor(score) {
    if (score >= 85) return '#22c55e';
    if (score >= 70) return '#84cc16';
    if (score >= 55) return '#eab308';
    if (score >= 40) return '#f97316';
    return '#ef4444';
}

function populateAngleTable(angleDifferences) {
    const tbody = document.getElementById('angle-table-body');
    tbody.innerHTML = '';

    const sortedKeys = Object.keys(angleDifferences).sort((a, b) => {
        const diffA = angleDifferences[a].difference || 0;
        const diffB = angleDifferences[b].difference || 0;
        return diffB - diffA;
    });

    sortedKeys.forEach(key => {
        const diff = angleDifferences[key];
        const tr = document.createElement('tr');

        let diffClass = 'normal';
        let diffValue = '-';

        if (diff.difference !== null && diff.difference !== undefined) {
            diffValue = diff.difference.toFixed(1) + '°';
            if (diff.difference >= 30) diffClass = 'danger';
            else if (diff.difference >= 15) diffClass = 'warning';
        }

        tr.innerHTML = `
            <td>${diff.name}</td>
            <td>${diff.standard !== null ? diff.standard.toFixed(1) + '°' : '-'}</td>
            <td>${diff.practice !== null ? diff.practice.toFixed(1) + '°' : '-'}</td>
            <td class="angle-diff ${diffClass}">${diffValue}</td>
            <td>${diff.weight || '-'}</td>
        `;

        tbody.appendChild(tr);
    });
}

function initDetailsToggle() {
    const toggle = document.getElementById('details-toggle');
    const content = document.getElementById('details-content');

    toggle.addEventListener('click', () => {
        const isOpen = content.style.display !== 'none';
        content.style.display = isOpen ? 'none' : 'block';
        toggle.classList.toggle('open', !isOpen);
    });
}

function showError(message) {
    const errorBox = document.getElementById('error-message');
    errorBox.textContent = message;
    errorBox.style.display = 'block';
    errorBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideError() {
    document.getElementById('error-message').style.display = 'none';
}
