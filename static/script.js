document.addEventListener('DOMContentLoaded', () => {
    const addJobForm = document.getElementById('add-job-form');
    const jobsTableBody = document.querySelector('#jobs-table tbody');
    const calculateBtn = document.getElementById('calculate-schedule-btn');
    const scheduleOutputCard = document.getElementById('schedule-output-card');
    const scheduleOutput = document.getElementById('schedule-output');

    const API_URL = window.location.origin;

    // --- Functions to interact with the API ---

    async function fetchJobs() {
        try {
            const response = await fetch(`${API_URL}/jobs`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const jobs = await response.json();
            renderJobs(jobs);
        } catch (error) {
            console.error("Failed to fetch jobs:", error);
            alert("Failed to load jobs. Please check the console for more details.");
        }
    }

    async function addJob(jobData) {
        try {
            const response = await fetch(`${API_URL}/jobs`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(jobData),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to add job');
            }
            // Refresh the jobs list to show the new job
            fetchJobs();
        } catch (error) {
            console.error("Failed to add job:", error);
            alert(`Error adding job: ${error.message}`);
        }
    }

    async function calculateSchedule() {
        try {
            // For simplicity, we'll use a fixed date range for the request
            const today = new Date();
            const endDate = new Date();
            endDate.setDate(today.getDate() + 30); // Schedule for the next 30 days

            const requestBody = {
                start_date: today.toISOString().split('T')[0],
                end_date: endDate.toISOString().split('T')[0],
            };

            const response = await fetch(`${API_URL}/schedule/calculate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to calculate schedule');
            }
            const result = await response.json();
            renderSchedule(result.schedule);
        } catch (error) {
            console.error("Failed to calculate schedule:", error);
            alert(`Error calculating schedule: ${error.message}`);
        }
    }


    // --- Functions to render data to the DOM ---

    function renderJobs(jobs) {
        jobsTableBody.innerHTML = ''; // Clear existing rows
        if (jobs.length === 0) {
            jobsTableBody.innerHTML = '<tr><td colspan="5">No jobs added yet.</td></tr>';
            return;
        }
        jobs.forEach(job => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${job.item}</td>
                <td>${job.name}</td>
                <td>${job.pieces_per_hour}</td>
                <td>${job.total_pieces}</td>
                <td>${job.required_hours.toFixed(2)}</td>
            `;
            jobsTableBody.appendChild(row);
        });
    }

    function renderSchedule(schedule) {
        scheduleOutput.innerHTML = ''; // Clear previous output
        if (Object.keys(schedule).length === 0) {
            scheduleOutput.innerHTML = '<p>No schedule could be generated. There might be no jobs or no working days in the period.</p>';
        }

        const sortedDates = Object.keys(schedule).sort();

        sortedDates.forEach(dateStr => {
            const tasks = schedule[dateStr];
            const dayDiv = document.createElement('div');
            dayDiv.className = 'day-schedule';

            const dateObj = new Date(dateStr);
            const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'long', timeZone: 'UTC' });

            let tasksHtml = '<ul>';
            if (tasks.length > 0) {
                tasks.forEach(task => {
                    tasksHtml += `<li><strong>${task.name}</strong>: ${task.hours_worked.toFixed(2)} hours</li>`;
                });
            } else {
                tasksHtml += '<li>No tasks scheduled.</li>';
            }
            tasksHtml += '</ul>';

            dayDiv.innerHTML = `<h3>${dayName}, ${dateStr}</h3>${tasksHtml}`;
            scheduleOutput.appendChild(dayDiv);
        });

        scheduleOutputCard.style.display = 'block'; // Show the card
    }

    // --- Event Listeners ---

    addJobForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const jobData = {
            item: document.getElementById('item').value,
            name: document.getElementById('name').value,
            pieces_per_hour: parseInt(document.getElementById('pieces_per_hour').value, 10),
            total_pieces: parseInt(document.getElementById('total_pieces').value, 10),
        };
        addJob(jobData);
        addJobForm.reset();
    });

    calculateBtn.addEventListener('click', () => {
        calculateSchedule();
    });

    // --- Initial Load ---
    fetchJobs();
});
