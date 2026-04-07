/* ============================================================
   HireSight — Charts JS (Chart.js powered)
   ============================================================ */

(function () {
  const BLUE  = '#3B82F6';
  const NAVY  = '#1E3A8A';
  const SKY   = '#60A5FA';
  const LIGHT = '#BFDBFE';
  const SURFACE = '#F1F5F9';

  /* ── Default chart options ───────────────────────────────── */
  const defaultFont = { family: "'DM Sans', sans-serif", size: 13 };
  Chart.defaults.font = defaultFont;
  Chart.defaults.color = '#64748B';
  Chart.defaults.plugins.legend.labels.boxWidth = 12;
  Chart.defaults.plugins.legend.labels.padding = 16;
  Chart.defaults.plugins.tooltip.padding = 10;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.plugins.tooltip.backgroundColor = '#1E3A8A';
  Chart.defaults.plugins.tooltip.titleFont = { ...defaultFont, weight: '700' };

  /* ── Data ────────────────────────────────────────────────── */
  const barData = {
    labels: ['Python', 'SQL', 'Power BI', 'Tableau', 'Machine Learning', 'Excel', 'R', 'Spark', 'Pandas', 'TensorFlow'],
    values: [88, 82, 76, 74, 69, 65, 58, 54, 51, 47],
  };

  const pieData = {
    labels: ['Data Engineering', 'Analytics', 'Machine Learning', 'Visualization', 'Statistics', 'Other'],
    values: [28, 24, 19, 14, 10, 5],
  };

  const trendMonths = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb'];
  const trendData = {
    labels: trendMonths,
    datasets: [
      { label: 'Python',   data: [72, 75, 78, 81, 85, 88], borderColor: BLUE,   backgroundColor: 'rgba(59,130,246,.1)',  tension: .4, fill: true },
      { label: 'Tableau',  data: [60, 63, 65, 69, 71, 74], borderColor: '#10B981', backgroundColor: 'rgba(16,185,129,.08)', tension: .4, fill: true },
      { label: 'Power BI', data: [55, 58, 62, 67, 73, 76], borderColor: '#F59E0B', backgroundColor: 'rgba(245,158,11,.08)', tension: .4, fill: true },
    ]
  };

  /* ── Bar Chart — Top Skills ──────────────────────────────── */
  function initBarChart() {
    const ctx = document.getElementById('barChart');
    if (!ctx) return;
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: barData.labels,
        datasets: [{
          label: 'Demand Score',
          data: barData.values,
          backgroundColor: barData.values.map((_, i) =>
            i < 3 ? `rgba(30,58,138,${.85 - i * .12})` : `rgba(59,130,246,${.8 - i * .06})`),
          borderRadius: 6,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` Demand Score: ${ctx.raw}/100`
            }
          }
        },
        scales: {
          x: {
            max: 100,
            grid: { color: 'rgba(226,232,240,.6)' },
            ticks: { callback: v => v + '%' }
          },
          y: {
            grid: { display: false },
          }
        },
        animation: {
          duration: 1000,
          easing: 'easeOutQuart',
        }
      }
    });
  }

  /* ── Pie/Doughnut Chart — Skill Categories ───────────────── */
  function initPieChart() {
    const ctx = document.getElementById('pieChart');
    if (!ctx) return;
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: pieData.labels,
        datasets: [{
          data: pieData.values,
          backgroundColor: [NAVY, BLUE, SKY, LIGHT, '#93C5FD', '#DBEAFE'],
          borderWidth: 0,
          hoverOffset: 8,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { padding: 14, usePointStyle: true, pointStyleWidth: 10 }
          },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.label}: ${ctx.raw}%`
            }
          }
        },
        animation: { duration: 1000, easing: 'easeOutQuart' }
      }
    });
  }

  /* ── Line Chart — Skill Trends ───────────────────────────── */
  function initTrendChart() {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;
    new Chart(ctx, {
      type: 'line',
      data: trendData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { position: 'top' },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.dataset.label}: ${ctx.raw}%`
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(226,232,240,.5)' },
          },
          y: {
            min: 40,
            max: 100,
            grid: { color: 'rgba(226,232,240,.5)' },
            ticks: { callback: v => v + '%' }
          }
        },
        elements: {
          point: { radius: 4, hoverRadius: 7, borderWidth: 2 }
        },
        animation: { duration: 1200, easing: 'easeOutQuart' }
      }
    });
  }

  /* ── Emerging skills ticker ──────────────────────────────── */
  function initEmergingSkills() {
    const container = document.getElementById('emergingSkillsList');
    if (!container) return;
    const skills = [
      { name: 'LLM Fine-tuning', growth: '+142%', badge: 'badge-blue' },
      { name: 'dbt (Data Build Tool)', growth: '+98%', badge: 'badge-green' },
      { name: 'Vector Databases', growth: '+87%', badge: 'badge-blue' },
      { name: 'Polars', growth: '+76%', badge: 'badge-green' },
      { name: 'DuckDB', growth: '+65%', badge: 'badge-blue' },
      { name: 'Prompt Engineering', growth: '+120%', badge: 'badge-amber' },
    ];
    skills.forEach(({ name, growth, badge }, i) => {
      const el = document.createElement('div');
      el.style.cssText = 'display:flex;align-items:center;justify-content:space-between;padding:.85rem 1rem;background:white;border:1px solid var(--border);border-radius:var(--radius);margin-bottom:.55rem;animation:fadeUp .5s both;animation-delay:' + (i * .07) + 's;transition:all .22s;cursor:default;';
      el.innerHTML = `
        <div style="display:flex;align-items:center;gap:.65rem;">
          <span style="font-weight:700;color:var(--muted);font-size:.78rem;width:18px;text-align:center;">${i + 1}</span>
          <span style="font-size:.9rem;font-weight:600;color:var(--text);">${name}</span>
        </div>
        <span class="badge ${badge}" style="font-size:.78rem;">↑ ${growth}</span>`;
      el.addEventListener('mouseenter', () => { el.style.borderColor = 'rgba(59,130,246,.3)'; el.style.transform = 'translateX(3px)'; });
      el.addEventListener('mouseleave', () => { el.style.borderColor = 'var(--border)'; el.style.transform = ''; });
      container.appendChild(el);
    });
  }

  /* ── Init ────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', () => {
    initBarChart();
    initPieChart();
    initTrendChart();
    initEmergingSkills();
  });
})();
