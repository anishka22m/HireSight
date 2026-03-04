/* ============================================================
   HireSight — Results Page JS
   ============================================================ */

(function () {
  /* ── Mock data ───────────────────────────────────────────── */
  const data = {
    score: 84,
    role: 'Data Analyst',
    matchedSkills: [
      { name: 'Python', level: 92 },
      { name: 'SQL', level: 88 },
      { name: 'Pandas', level: 85 },
      { name: 'Data Visualization', level: 78 },
      { name: 'Statistical Analysis', level: 75 },
      { name: 'Excel', level: 70 },
      { name: 'NumPy', level: 68 },
    ],
    missingSkills: [
      { name: 'Tableau', priority: 'high' },
      { name: 'Power BI', priority: 'high' },
      { name: 'Machine Learning', priority: 'medium' },
      { name: 'Spark', priority: 'medium' },
      { name: 'R Language', priority: 'low' },
    ],
    suggestions: [
      { icon: '🎯', title: 'Add Tableau to your skillset', text: 'Tableau appears in 74% of Data Analyst job postings. Completing a beginner course could significantly boost your score.' },
      { icon: '📊', title: 'Include Power BI experience', text: 'Power BI is a top requested BI tool. Even basic proficiency stands out to employers.' },
      { icon: '🤖', title: 'Explore Machine Learning basics', text: 'Foundational ML knowledge is increasingly expected for senior data roles.' },
      { icon: '✍️', title: 'Quantify your achievements', text: 'Add metrics to your work experience (e.g. "Reduced report time by 40%") for stronger impact.' },
    ]
  };

  /* ── Gauge ───────────────────────────────────────────────── */
  function initGauge() {
    const circle = document.getElementById('gaugeCircle');
    const scoreEl = document.getElementById('scoreNum');
    const labelEl = document.getElementById('scoreLabel');
    if (!circle) return;

    const r = 80;
    const circumference = 2 * Math.PI * r;
    circle.setAttribute('stroke-dasharray', circumference);
    circle.setAttribute('stroke-dashoffset', circumference);

    const target = data.score;
    let color = '#EF4444';
    let label = 'Needs Work';
    if (target >= 80) { color = '#10B981'; label = 'Excellent'; }
    else if (target >= 60) { color = '#F59E0B'; label = 'Good'; }
    else if (target >= 40) { color = '#3B82F6'; label = 'Fair'; }
    circle.style.stroke = color;
    if (labelEl) { labelEl.textContent = label; labelEl.style.color = color; }

    // Animate
    setTimeout(() => {
      const offset = circumference - (target / 100) * circumference;
      circle.style.transition = 'stroke-dashoffset 1.4s cubic-bezier(.4,0,.2,1)';
      circle.style.strokeDashoffset = offset;

      // Count up score number
      let current = 0;
      const step = () => {
        current = Math.min(current + 2, target);
        if (scoreEl) scoreEl.textContent = current;
        if (current < target) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    }, 600);
  }

  /* ── Skill bars ──────────────────────────────────────────── */
  function buildMatchedSkills() {
    const container = document.getElementById('matchedSkillsList');
    if (!container) return;
    data.matchedSkills.forEach(({ name, level }, i) => {
      const div = document.createElement('div');
      div.style.cssText = 'margin-bottom:1rem;animation:fadeUp .5s both;animation-delay:' + (i * .07) + 's';
      div.innerHTML = `
        <div style="display:flex;justify-content:space-between;margin-bottom:.35rem;">
          <span style="font-size:.88rem;font-weight:600;color:var(--text)">${name}</span>
          <span style="font-size:.82rem;color:var(--muted)">${level}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" data-width="${level}" style="width:0%"></div>
        </div>`;
      container.appendChild(div);
    });
  }

  function buildMissingSkills() {
    const container = document.getElementById('missingSkillsList');
    if (!container) return;
    data.missingSkills.forEach(({ name, priority }, i) => {
      const pill = document.createElement('div');
      const badgeClass = priority === 'high' ? 'badge-red' : priority === 'medium' ? 'badge-amber' : 'badge-blue';
      const dot = priority === 'high' ? '🔴' : priority === 'medium' ? '🟡' : '🔵';
      pill.style.cssText = 'display:flex;align-items:center;justify-content:space-between;padding:.75rem 1rem;background:white;border:1px solid var(--border);border-radius:var(--radius);margin-bottom:.6rem;animation:fadeUp .5s both;animation-delay:' + (i * .08) + 's';
      pill.innerHTML = `
        <span style="font-size:.88rem;font-weight:600;color:var(--text)">${dot} ${name}</span>
        <span class="badge ${badgeClass}" style="font-size:.72rem;text-transform:capitalize;">${priority}</span>`;
      container.appendChild(pill);
    });
  }

  function buildSuggestions() {
    const container = document.getElementById('suggestionsList');
    if (!container) return;
    data.suggestions.forEach(({ icon, title, text }, i) => {
      const card = document.createElement('div');
      card.style.cssText = 'display:flex;gap:1rem;padding:1.25rem;background:white;border:1px solid var(--border);border-radius:var(--radius-lg);margin-bottom:.85rem;box-shadow:var(--shadow-sm);animation:fadeUp .5s both;animation-delay:' + (i * .1) + 's;transition:box-shadow .22s,transform .22s;';
      card.innerHTML = `
        <div style="font-size:1.6rem;flex-shrink:0;margin-top:.1rem;">${icon}</div>
        <div>
          <h4 style="margin-bottom:.3rem;">${title}</h4>
          <p style="font-size:.875rem;">${text}</p>
        </div>`;
      card.addEventListener('mouseenter', () => { card.style.boxShadow = 'var(--shadow-lg)'; card.style.transform = 'translateY(-2px)'; });
      card.addEventListener('mouseleave', () => { card.style.boxShadow = 'var(--shadow-sm)'; card.style.transform = ''; });
      container.appendChild(card);
    });
  }

  function animateBars() {
    setTimeout(() => {
      document.querySelectorAll('.progress-fill[data-width]').forEach(el => {
        el.style.transition = 'width 1s cubic-bezier(.4,0,.2,1)';
        el.style.width = el.dataset.width + '%';
      });
    }, 400);
  }

  /* ── Init ────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', () => {
    initGauge();
    buildMatchedSkills();
    buildMissingSkills();
    buildSuggestions();
    animateBars();
  });
})();
