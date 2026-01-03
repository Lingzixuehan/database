document.addEventListener('DOMContentLoaded', () => {
    const roadSelect = document.getElementById('event-road');
    const form = document.getElementById('event-form');
    const feedback = document.getElementById('event-feedback');
    const tableBody = document.querySelector('#events-timeline-table tbody');

    function showMessage(message, type = 'success') {
        feedback.textContent = message;
        feedback.className = `mt-3 small text-${type}`;
    }

    function fetchRoads() {
        fetch('/api/roads')
            .then(response => response.json())
            .then(data => {
                roadSelect.innerHTML = '';
                data.forEach(road => {
                    const option = document.createElement('option');
                    option.value = road.id;
                    option.textContent = `${road.name} (${road.code})`;
                    roadSelect.appendChild(option);
                });
            })
            .catch(() => showMessage('无法加载道路列表', 'danger'));
    }

    function fetchEvents() {
        fetch('/api/events?status=all&limit=50')
            .then(response => response.json())
            .then(data => {
                tableBody.innerHTML = '';
                if (!data.length) {
                    tableBody.innerHTML = '<tr><td colspan="5">No events recorded.</td></tr>';
                    return;
                }
                data.forEach(event => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${new Date(event.timestamp).toLocaleString()}</td>
                        <td>${event.road_name ?? 'Unknown'}</td>
                        <td>${event.type}</td>
                        <td><span class="badge bg-${event.status === 'active' ? 'danger' : 'secondary'}">${event.status}</span></td>
                        <td>${event.severity ?? '--'}</td>
                    `;
                    tableBody.appendChild(row);
                });
            })
            .catch(() => showMessage('无法加载事件列表', 'danger'));
    }

    form.addEventListener('submit', event => {
        event.preventDefault();
        const payload = {
            road_id: Number(roadSelect.value),
            type: document.getElementById('event-type').value,
            status: document.getElementById('event-status').value,
            severity: Number(document.getElementById('event-severity').value) || null,
            position: document.getElementById('event-position').value || null,
            description: document.getElementById('event-description').value || null,
        };

        fetch('/api/events', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Failed to create event');
                    });
                }
                return response.json();
            })
            .then(data => {
                showMessage('事件已创建！', 'success');
                form.reset();
                fetchEvents();
            })
            .catch(error => showMessage(error.message, 'danger'));
    });

    fetchRoads();
    fetchEvents();
});
