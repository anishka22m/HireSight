/* ============================================================
   HireSight — Upload Page JS
   ============================================================ */

(function () {
  const dropzone  = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const browseBtn = document.getElementById('browseBtn');
  const filePreview    = document.getElementById('filePreview');
  const fileName       = document.getElementById('fileName');
  const fileSize       = document.getElementById('fileSize');
  const fileTypeIcon   = document.getElementById('fileTypeIcon');
  const removeBtn      = document.getElementById('removeBtn');
  const analyzeBtn     = document.getElementById('analyzeBtn');
  const progressSection= document.getElementById('progressSection');
  const progressFill   = document.getElementById('progressFill');
  const progressPercent= document.getElementById('progressPercent');
  const progressStatus = document.getElementById('progressStatus');
  const uploadSection  = document.getElementById('uploadSection');
  const errorMsg       = document.getElementById('errorMsg');

  const ALLOWED_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword'
  ];
  const ALLOWED_EXT = ['.pdf', '.docx', '.doc'];
  const MAX_SIZE_MB  = 10;

  let selectedFile = null;

  /* ── Helpers ─────────────────────────────────────────────── */
  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function getExt(name) {
    return name.substring(name.lastIndexOf('.')).toLowerCase();
  }

  function isValidFile(file) {
    const ext = getExt(file.name);
    if (!ALLOWED_EXT.includes(ext)) return false;
    if (file.size > MAX_SIZE_MB * 1024 * 1024) return false;
    return true;
  }

  function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.style.display = 'flex';
    setTimeout(() => { errorMsg.style.display = 'none'; }, 4000);
  }

  /* ── File accepted ───────────────────────────────────────── */
  function acceptFile(file) {
    if (!isValidFile(file)) {
      if (getExt(file.name) && !ALLOWED_EXT.includes(getExt(file.name))) {
        showError('Invalid file type. Please upload a PDF or DOCX file.');
      } else {
        showError(`File too large. Maximum size is ${MAX_SIZE_MB} MB.`);
      }
      return;
    }
    selectedFile = file;
    const ext = getExt(file.name);
    fileTypeIcon.textContent = ext === '.pdf' ? '📄' : '📝';
    fileName.textContent = file.name;
    fileSize.textContent = formatBytes(file.size);

    filePreview.style.display = 'flex';
    dropzone.style.border = '1.5px solid var(--success)';
    analyzeBtn.disabled = false;
    analyzeBtn.classList.add('ready');
    errorMsg.style.display = 'none';
  }

  /* ── Drag & drop ─────────────────────────────────────────── */
  ['dragenter', 'dragover'].forEach(ev => {
    dropzone.addEventListener(ev, e => {
      e.preventDefault();
      dropzone.classList.add('drag-active');
    });
  });
  ['dragleave', 'drop'].forEach(ev => {
    dropzone.addEventListener(ev, e => {
      e.preventDefault();
      dropzone.classList.remove('drag-active');
    });
  });
  dropzone.addEventListener('drop', e => {
    const file = e.dataTransfer.files[0];
    if (file) acceptFile(file);
  });

  /* ── Browse ──────────────────────────────────────────────── */
  browseBtn.addEventListener('click', () => fileInput.click());
  dropzone.addEventListener('click', e => {
    if (e.target === dropzone || e.target.closest('.drop-area-inner')) fileInput.click();
  });
  fileInput.addEventListener('change', e => {
    if (e.target.files[0]) acceptFile(e.target.files[0]);
  });

  /* ── Remove ──────────────────────────────────────────────── */
  removeBtn.addEventListener('click', e => {
    e.stopPropagation();
    selectedFile = null;
    fileInput.value = '';
    filePreview.style.display = 'none';
    dropzone.style.border = '';
    analyzeBtn.disabled = true;
    analyzeBtn.classList.remove('ready');
  });

  /* ── Analyze ─────────────────────────────────────────────── */
/* ── Analyze ─────────────────────────────────────────────── */
analyzeBtn.addEventListener('click', startAnalysis);

async function startAnalysis() {
  if (!selectedFile) return;

  const formData = new FormData();
  formData.append("file", selectedFile); // The key "file" must match server.py

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      body: formData
    });

    if (!response.ok) throw new Error("Server error");

    try {
  const response = await fetch("/api/analyze", {
    method: "POST",
    body: formData
  });

  const result = await response.json();

  // ✅ HANDLE BACKEND ERROR
  if (!response.ok || result.error) {
    showError(result.error || "Invalid resume uploaded.");
    return;
  }

  // Save result
  localStorage.setItem("analysisResult", JSON.stringify(result));

  window.location.href = "/results";

} catch (error) {
  console.error("Analysis failed:", error);
  showError("Analysis failed. Please try again.");
}
    
    // Save to localStorage so results.html can read it
    localStorage.setItem("analysisResult", JSON.stringify(result));

    // Redirect to the results page
    window.location.href = "/results"; 
  } catch (error) {
    console.error("Analysis failed:", error);
    showError("Analysis failed. Please try again.");
  }
}

  const stages = [
    { pct: 15, msg: 'Uploading resume…' },
    { pct: 35, msg: 'Parsing document content…' },
    { pct: 55, msg: 'Extracting skills & experience…' },
    { pct: 72, msg: 'Comparing with market data…' },
    { pct: 88, msg: 'Generating insights…' },
    { pct: 100, msg: 'Analysis complete! Redirecting…' },
  ];

  function simulateProgress() {
    let idx = 0;
    function step() {
      if (idx >= stages.length) {
        setTimeout(() => { window.location.href = 'results.html'; }, 700);
      }
      const { pct, msg } = stages[idx];
      progressFill.style.width = pct + '%';
      progressPercent.textContent = pct + '%';
      progressStatus.textContent = msg;
      idx++;
      setTimeout(step, 700 + Math.random() * 400);
    }
    step();
  }
})();
