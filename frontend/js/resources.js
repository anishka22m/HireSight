/* ============================================================
   HireSight — Finalized Resources Logic (Integrated)
   ============================================================ */

(function () {
    const COURSES_API_URL = "/api/resources";
    const ROADMAP_API_URL = "/api/roadmap";

    async function initResources() {
        const gapContainer = document.getElementById('gapPills');
        const courseGrid = document.getElementById('coursesGrid');
        const gapTitle = document.getElementById('gapTitle');
        const gapDesc = document.getElementById('gapDesc');
        const uploadCTA = document.getElementById('uploadCTA');
        
        // 1. Get stored analysis result from localStorage
        const stored = localStorage.getItem("analysisResult");
        
        if (!stored) {
            console.log("No analysis found. Keeping default state.");
            if (uploadCTA) uploadCTA.style.display = 'block';
            return; 
        }

        if (uploadCTA) uploadCTA.style.display = 'none';

        const data = JSON.parse(stored);
        const missing = data.missing_skills || [];
        const domain = data.role || "Technology";

        // 2. Update dynamic text
        if (gapTitle) gapTitle.textContent = `${missing.length} High-Priority Skills to Learn`;
        if (gapDesc) gapDesc.textContent = `Based on your resume analysis, these skills are the critical gaps between your profile and current ${domain} roles.`;

        // 3. Update the pills
        if (gapContainer) {
            gapContainer.innerHTML = '';
            missing.forEach((skill, i) => {
                const pill = document.createElement('div');
                pill.className = 'gap-pill';
                const icon = i < 2 ? '🔴' : (i < 4 ? '🟡' : '🔵');
                pill.textContent = `${icon} ${skill.name}`;
                gapContainer.appendChild(pill);
            });
        }

        // 4. Fetch Quick Courses
        if (missing.length > 0) {
            const skillNames = missing.map(s => s.name);
            await fetchResources(skillNames, domain, courseGrid);
            
            // Setup Roadmap Button
            setupRoadmapGenerator(data, skillNames);
        }
    }

    // --- QUICK COURSES LOGIC ---
    async function fetchResources(skills, domain, container) {
        try {
            const response = await fetch(COURSES_API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ missing_skills: skills, domain: domain })
            });
            const result = await response.json();

            if (result.status === "success" && result.resources.length > 0) {
                container.innerHTML = ''; 
                result.resources.forEach(course => {
                    const card = document.createElement('div');
                    card.className = 'card course-card anim-fade-up';
                    
                    const platform = course.provider.toLowerCase();
                    let dotStyle = "background:#EEF2FF; color:#4F46E5;"; 
                    let dotLetter = course.provider[0];

                    if (platform.includes('linkedin')) { dotStyle = "background:#E7F3FF; color:#0077B5;"; dotLetter = 'in'; }
                    else if (platform.includes('udemy')) { dotStyle = "background:#FFF4E6; color:#E8831B;"; dotLetter = 'U'; }
                    else if (platform.includes('coursera')) { dotStyle = "background:#F0FFF4; color:#38A169;"; dotLetter = 'Co'; }
                    else if (platform.includes('youtube')) { dotStyle = "background:#FFEBEE; color:#FF0000;"; dotLetter = 'Yt'; }

                    card.innerHTML = `
                        <div class="course-badge-row">
                          <div class="course-platform">
                            <div class="platform-dot" style="${dotStyle}">${dotLetter}</div>
                            ${course.provider}
                          </div>
                          <span class="badge badge-blue">${course.related_skill}</span>
                        </div>
                        <h4>${course.title}</h4>
                        <p>Learn ${course.related_skill} to bridge the gap for ${domain} roles. Highly rated by professionals.</p>
                        <div class="course-meta">
                          <span><span class="stars">★★★★★</span> ${course.rating}</span>
                        </div>
                        <div class="course-footer">
                          <span class="course-price ${course.price.toLowerCase().includes('free') ? 'free' : ''}">${course.price}</span>
                          <a href="${course.url}" target="_blank" class="course-cta">Enroll →</a>
                        </div>
                    `;
                    container.appendChild(card);
                });
            } else {
                container.innerHTML = '<p style="grid-column:1/-1; text-align:center;">No specific courses found for your gaps.</p>';
            }
        } catch (e) {
            container.innerHTML = '<p style="grid-column:1/-1; text-align:center; color:red;">Unable to load resources.</p>';
        }
    }

    // --- AI SPRINT ROADMAP LOGIC ---
    function setupRoadmapGenerator(resumeData, missingSkillNames) {
        const btn = document.getElementById('generateRoadmapBtn');
        if (!btn) return;

        btn.addEventListener('click', async () => {
            // 1. Show Loading State (AI takes a few seconds)
            btn.innerHTML = `<span style="opacity: 0.7;">Synthesizing Curriculum...</span>`;
            btn.style.pointerEvents = 'none';

            // 2. Build the "Contextual Vector" (User Profile)
            const existingSkills = resumeData.found_skills ? resumeData.found_skills.map(s => s.name) : ["General IT Skills"];
            const domain = resumeData.role || "Technology";

            const payload = {
                domain: domain,
                user_level: "Student/Fresher",
                existing_skills: existingSkills,
                missing_skills: missingSkillNames,
                target_role: domain + " Professional",
                market_context: { trending_skills: missingSkillNames, demand_level: "High" },
                constraints: { duration: "7 days", learning_style: "Project-based, hands-on" }
            };

            // 3. Call the AI Endpoint
            try {
                const response = await fetch(ROADMAP_API_URL, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const result = await response.json();

                if (result.status === "success") {
                    renderRoadmap(result.roadmap);
                } else {
                    alert("Error generating roadmap: " + result.message);
                    btn.innerHTML = "Generate 7-Day Sprint →";
                    btn.style.pointerEvents = 'auto';
                }
            } catch (error) {
                console.error(error);
                alert("Failed to connect to the server.");
                btn.innerHTML = "Generate 7-Day Sprint →";
                btn.style.pointerEvents = 'auto';
            }
        });
    }

    function renderRoadmap(data) {
        document.getElementById('roadmapPrompt').style.display = 'none';
        const resultContainer = document.getElementById('roadmapResult');
        resultContainer.style.display = 'block';

        // Build the HTML for the Timeline
        let daysHtml = data.daily_plan.map(day => `
            <div style="display: flex; gap: 1.5rem; margin-bottom: 1.5rem;">
                <div style="flex-shrink: 0; width: 50px; height: 50px; background: #EFF6FF; color: #3B82F6; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem;">
                    D${day.day}
                </div>
                <div class="card" style="flex-grow: 1; padding: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0; color: var(--navy);">${day.focus}</h4>
                        <span class="badge badge-navy">${day.time_commitment}</span>
                    </div>
                    <ul style="margin: 0; padding-left: 1.2rem; color: var(--muted); font-size: 0.9rem;">
                        ${day.action_items.map(item => `<li style="margin-bottom: 0.3rem;">${item}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `).join('');

        resultContainer.innerHTML = `
            <div class="card" style="padding: 2rem; border-left: 4px solid var(--blue); margin-bottom: 2rem;">
                <h3 style="margin-bottom: 0.5rem;">${data.sprint_title}</h3>
                <p style="color: var(--muted); font-size: 0.95rem;">${data.synthesis_overview}</p>
            </div>
            
            <div style="margin-bottom: 3rem;">
                <h4 style="margin-bottom: 1.5rem;">Your Daily Action Plan</h4>
                ${daysHtml}
            </div>

            <div class="card" style="padding: 2rem; background: linear-gradient(135deg, #F8FAFC, #EFF6FF);">
                <div class="section-label" style="margin-bottom: 0.5rem;">Final Capstone Project</div>
                <h3 style="margin-bottom: 0.5rem;">${data.capstone_project.title}</h3>
                <p style="font-size: 0.95rem; margin-bottom: 1rem;">${data.capstone_project.description}</p>
                <div style="background: white; padding: 1rem; border-radius: var(--radius); font-size: 0.85rem; border: 1px solid var(--border);">
                    <strong>Portfolio Value:</strong> ${data.capstone_project.portfolio_value}
                </div>
            </div>
        `;
    }

    document.addEventListener('DOMContentLoaded', initResources);
})();