/* ============================================================
   HireSight — Results Page JS (Final Integrated Version)
   ============================================================ */

(function () {

  /* ── Load Real Analysis Data ───────────────────────────── */
  const data = JSON.parse(localStorage.getItem("analysisResult"));

  if (!data) {
    console.error("No analysis data found.");
    return;
  }

  /* ── NEW: Update Header & Mini Stats ────────────────────── */
  function updateHeaderStats() {
    // 1. Update Role Badge and Descriptions
    const roleBadge = document.getElementById('roleBadge');
    const scoreDesc = document.getElementById('scoreDescription');
    
    if (roleBadge) roleBadge.textContent = data.role;
    if (scoreDesc) scoreDesc.textContent = `Your resume is highly competitive for ${data.role} roles.`;

    // 2. Update Mini Stat Numbers
    const matchedCountEl = document.getElementById('matchedCount');
    const missingCountEl = document.getElementById('missingCount');
    const priorityCountEl = document.getElementById('priorityCount');
    const suggestionCountEl = document.getElementById('suggestionCount');

    if (matchedCountEl) matchedCountEl.textContent = data.matched_count;
    if (missingCountEl) missingCountEl.textContent = data.missing_count;
    if (priorityCountEl) priorityCountEl.textContent = data.high_priority_count;
    if (suggestionCountEl) suggestionCountEl.textContent = data.suggestions.length;

    // 3. Update Tab Button Labels
    const matchedTabBtn = document.getElementById('matchedTabBtn');
    const missingTabBtn = document.getElementById('missingTabBtn');

    if (matchedTabBtn) matchedTabBtn.textContent = `✅ Matched Skills (${data.matched_count})`;
    if (missingTabBtn) missingTabBtn.textContent = `⚠️ Missing Skills (${data.missing_count})`;
  }

  /* ── Gauge ─────────────────────────────────────────────── */
  function initGauge() {
    const circle = document.getElementById('gaugeCircle');
    const scoreEl = document.getElementById('scoreNum');
    const labelEl = document.getElementById('scoreLabel');

    if (!circle) return;

    const r = 80;
    const circumference = 2 * Math.PI * r;

    circle.setAttribute('stroke-dasharray', circumference);
    circle.setAttribute('stroke-dashoffset', circumference);

    const target = Math.round(data.score); // Round for clean UI

    let color = '#EF4444';
    let label = 'Needs Work';

    if (target >= 80) { color = '#10B981'; label = 'Excellent'; }
    else if (target >= 60) { color = '#F59E0B'; label = 'Good'; }
    else if (target >= 40) { color = '#3B82F6'; label = 'Fair'; }

    circle.style.stroke = color;

    if (labelEl) {
      labelEl.textContent = label;
      labelEl.style.color = color;
    }

    setTimeout(() => {
      const offset = circumference - (target / 100) * circumference;
      circle.style.transition = 'stroke-dashoffset 1.4s cubic-bezier(.4,0,.2,1)';
      circle.style.strokeDashoffset = offset;

      let current = 0;
      const step = () => {
        current = Math.min(current + 2, target);
        if (scoreEl) scoreEl.textContent = current;
        if (current < target) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    }, 600);
  }

  /* ── Matched Skills ─────────────────────────────────────── */
  function buildMatchedSkills() {
    const container = document.getElementById('matchedSkillsList');
    if (!container) return;

    data.matched_skills.forEach(({ name, level }, i) => {
      const div = document.createElement('div');
      div.style.cssText = 'margin-bottom:1rem;animation:fadeUp .5s both;animation-delay:' + (i * 0.07) + 's';

      div.innerHTML = `
        <div style="display:flex;justify-content:space-between;margin-bottom:.35rem;">
          <span style="font-size:.88rem;font-weight:600;color:var(--text)">${name}</span>
          <span style="font-size:.82rem;color:var(--muted)">${level}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" data-width="${level}" style="width:0%"></div>
        </div>
      `;
      container.appendChild(div);
    });
  }

  /* ── Missing Skills ─────────────────────────────────────── */
  function buildMissingSkills() {
    const container = document.getElementById('missingSkillsList');
    if (!container) return;

    data.missing_skills.forEach(({ name, priority }, i) => {
      const pill = document.createElement('div');
      const badgeClass = priority === 'high' ? 'badge-red' : priority === 'medium' ? 'badge-amber' : 'badge-blue';
      const dot = priority === 'high' ? '🔴' : priority === 'medium' ? '🟡' : '🔵';

      pill.style.cssText = 'display:flex;align-items:center;justify-content:space-between;padding:.75rem 1rem;background:white;border:1px solid var(--border);border-radius:var(--radius);margin-bottom:.6rem;animation:fadeUp .5s both;animation-delay:' + (i * 0.08) + 's';

      pill.innerHTML = `
        <span style="font-size:.88rem;font-weight:600;color:var(--text)">${dot} ${name}</span>
        <span class="badge ${badgeClass}" style="font-size:.72rem;text-transform:capitalize;">${priority}</span>
      `;
      container.appendChild(pill);
    });
  }

  /* ── Suggestions ───────────────────────────────────────── */
  function buildSuggestions() {
    const container = document.getElementById('suggestionsList');
    if (!container) return;

    data.suggestions.forEach(({ icon, title, text }, i) => {
      const card = document.createElement('div');
      card.style.cssText = 'display:flex;gap:1rem;padding:1.25rem;background:white;border:1px solid var(--border);border-radius:var(--radius-lg);margin-bottom:.85rem;box-shadow:var(--shadow-sm);animation:fadeUp .5s both;animation-delay:' + (i * 0.1) + 's;transition:box-shadow .22s,transform .22s;';

      card.innerHTML = `
        <div style="font-size:1.6rem;flex-shrink:0;margin-top:.1rem;">${icon}</div>
        <div>
          <h4 style="margin-bottom:.3rem;">${title}</h4>
          <p style="font-size:.875rem;">${text}</p>
        </div>
      `;
      container.appendChild(card);
    });
  }

  /* ── Animate Bars ──────────────────────────────────────── */
  function animateBars() {
    setTimeout(() => {
      document.querySelectorAll('.progress-fill[data-width]').forEach(el => {
        el.style.transition = 'width 1s cubic-bezier(.4,0,.2,1)';
        el.style.width = el.dataset.width + '%';
      });
    }, 400);
  }

  /* ── Init ───────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', () => {
    // Run the header update first so titles/counts are ready
    updateHeaderStats();
    
    // Run visual components
    initGauge();
    buildMatchedSkills();
    buildMissingSkills();
    buildSuggestions();
    animateBars();
  });

})();