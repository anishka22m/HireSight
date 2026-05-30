/* ============================================================
   HireSight — Dynamic Charts JS
   ============================================================ */

(function () {
  const BLUE = '#3B82F6';
  const NAVY = '#1E3A8A';
  const SKY = '#60A5FA';
  const LIGHT = '#BFDBFE';

  // Keep track of chart instances to destroy them before re-render
  let charts = {
    bar: null,
    pie: null,
    line: null
  };

/* -- API Data Fetching -- */
async function loadDashboardData(role = "All Roles") {
  try {
    const response = await fetch(`/api/trends?role=${encodeURIComponent(role)}`);
    const data = await response.json();

    // Update Dynamic Dates in UI
    const updatedTextEl = document.getElementById('uiLastUpdated');
    const topSkillsDateEl = document.getElementById('uiTopSkillsDate');
    
    if(updatedTextEl) updatedTextEl.textContent = `Updated ${data.current_month} · ${role}`;
    if(topSkillsDateEl) topSkillsDateEl.textContent = data.current_month;

    updateMiniStats(data.stats);
    renderBarChart(data.top_skills);
    renderPieChart(data.categories);
    renderTrendChart(data.trend_months, data.trends);
    
    renderEmergingSkills(data.emerging_list); 
    
  } catch (error) {
    console.error("Error loading market intelligence:", error);
  }
}
  /* -- UI Update: Mini Stats -- */
  function updateMiniStats(stats) {
    document.getElementById('statSkillsTracked').textContent = stats.skills_tracked.toLocaleString();
    document.getElementById('statJobsAnalyzed').textContent = stats.total_jobs.toLocaleString();
    document.getElementById('statEmergingCount').textContent = stats.emerging_skills;
  }

  /* -- Chart 1: Top Skills (Bar) -- */
  function renderBarChart(skills) {
    const ctx = document.getElementById('barChart');
    if (!ctx) return;
    if (charts.bar) charts.bar.destroy();

    charts.bar = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: skills.map(s => s.name),
        datasets: [{
          label: 'Demand %',
          data: skills.map(s => s.demand),
          backgroundColor: BLUE,
          borderRadius: 6,
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } }
      }
    });
  }

  /* -- Chart 2: Categories (Doughnut) -- */
  function renderPieChart(categories) {
    const ctx = document.getElementById('pieChart');
    if (!ctx) return;
    if (charts.pie) charts.pie.destroy();

    charts.pie = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: categories.map(c => c.label),
        datasets: [{
          data: categories.map(c => c.value),
          backgroundColor: [NAVY, BLUE, SKY, LIGHT, '#94A3B8'],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: { legend: { position: 'bottom' } }
      }
    });
  }

  /* -- Chart 3: Trends (Line) -- */
  function renderTrendChart(months, trendData) {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;
    if (charts.line) charts.line.destroy();

    const colors = [BLUE, '#10B981', '#F59E0B'];

    charts.line = new Chart(ctx, {
      type: 'line',
      data: {
        labels: months,
        datasets: trendData.map((t, i) => ({
          label: t.skill,
          data: t.values,
          borderColor: colors[i % colors.length],
          tension: 0.4,
          fill: false
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: false, ticks: { callback: v => v + '%' } } }
      }
    });
  }

  /* -- Filter Interaction -- */
  function initFilters() {
    // Select all filter buttons EXCEPT the refresh button
    const filterButtons = document.querySelectorAll('.dashboard-filters .filter-btn:not(#refreshDataBtn)');
    filterButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        // UI Visual Update
        filterButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Fetch new data based on role
        const selectedRole = btn.getAttribute('data-role');
        loadDashboardData(selectedRole);
      });
    });
  }
  // 1. Add this function to build the list items
function renderEmergingSkills(skills) {
  const container = document.getElementById('emergingSkillsList');
  if (!container) return;
  
  container.innerHTML = ''; // Clear previous list

  skills.forEach((skill, i) => {
    const el = document.createElement('div');
    el.style.cssText = `
      display:flex; align-items:center; justify-content:space-between; 
      padding:.85rem 1rem; background:white; border:1px solid var(--border); 
      border-radius:var(--radius); margin-bottom:.55rem; 
      animation:fadeUp .5s both; animation-delay:${i * .07}s;
    `;
    
    el.innerHTML = `
      <div style="display:flex; align-items:center; gap:.65rem;">
        <span style="font-weight:700; color:var(--muted); font-size:.78rem; width:18px;">${i + 1}</span>
        <span style="font-size:.9rem; font-weight:600; color:var(--text);">${skill.name}</span>
      </div>
      <span class="badge badge-green" style="font-size:.78rem;">↑ ${skill.growth}</span>
    `;
    container.appendChild(el);
  });
}

  /* -- Init -- */
/* -- Refresh Data Logic with Auto-Refresh Loader -- */
  function initRefreshLogic() {
    const refreshBtn = document.getElementById('refreshDataBtn');
    if (!refreshBtn) return;

    refreshBtn.addEventListener('click', async () => {
      // Grab the loader elements
      const loader = document.getElementById('globalLoader');
      const loaderTitle = document.getElementById('loaderTitle');
      const loaderDesc = document.getElementById('loaderDesc');

      try {
        // 1. Trigger the background script on the server
        await fetch('/api/refresh-trends', { method: 'POST' });
        
        // 2. Show the full screen loader
        if (loader) loader.style.display = 'flex';
        if (loaderTitle) loaderTitle.textContent = 'Updating Market Intelligence';
        
        // 3. Start a 75-second countdown to allow Groq to finish processing
        let timeLeft = 75; 
        if (loaderDesc) loaderDesc.textContent = `Scraping live job descriptions and running Llama 3.3. Auto-refreshing in ${timeLeft}s...`;

        const timer = setInterval(() => {
            timeLeft--;
            if (loaderDesc) loaderDesc.textContent = `Scraping live job descriptions and running Llama 3.3. Auto-refreshing in ${timeLeft}s...`;
            
            // 4. When the timer hits 0, force a page reload to fetch the new database entries!
            if(timeLeft <= 0) {
                clearInterval(timer);
                if (loaderDesc) loaderDesc.textContent = "Finalizing data... reloading now!";
                window.location.reload(); 
            }
        }, 1000);

      } catch (error) {
        console.error("Error triggering refresh:", error);
        if (loader) loader.style.display = 'none';
        alert("Failed to start refresh. Please check the server logs.");
      }
    });
  }

  /* -- Init -- */
  document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData(); // Initial load for All Roles
    initFilters();
    initRefreshLogic();
  });
})();