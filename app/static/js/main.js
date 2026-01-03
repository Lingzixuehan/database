document.addEventListener('DOMContentLoaded', () => {
    const trafficTbody = document.querySelector('#traffic-table tbody');
    const eventsTbody = document.querySelector('#events-table tbody');
    const historyForm = document.getElementById('history-form');
    const historyChartCtx = document.getElementById('history-chart').getContext('2d');
    const roadSelect = document.getElementById('road-select');
    const historyRoadSelect = document.getElementById('road-select-history');
    const historyEventsTbody = document.querySelector('#history-events-table tbody');
    const historyWindowInfo = document.getElementById('history-window-info');
    const historyChartContainer = document.querySelector('.chart-container');
    const summaryUpdatedAt = document.getElementById('summary-updated-at');
    const summaryTotalRoads = document.getElementById('summary-total-roads');
    const summaryActiveEvents = document.getElementById('summary-active-events');
    const summaryAvgSpeed = document.getElementById('summary-avg-speed');
    const summaryMaxVolume = document.getElementById('summary-max-volume');
    const summaryCongestedList = document.getElementById('summary-congested-list');
    const timelineList = document.getElementById('event-timeline');
    const roadDetailsName = document.getElementById('road-details-name');
    const roadDetailsMeta = document.getElementById('road-details-meta');
    const roadDetailsLatest = document.getElementById('road-details-latest');
    const roadDetailsAvgSpeed = document.getElementById('road-details-avg-speed');
    const roadDetailsAvgVolume = document.getElementById('road-details-avg-volume');
    const roadDetailsCongestion = document.getElementById('road-details-congestion');
    const roadDetailsEvents = document.getElementById('road-details-events');
    const alertCenter = document.getElementById('alert-center');
    const systemStatusList = document.getElementById('system-status-list');
    const systemStatusUpdated = document.getElementById('system-status-updated');
    const mapView = document.getElementById('map-view');
    const weeklyReportCards = document.getElementById('weekly-report-cards');
    const weeklyDownloadButton = document.getElementById('weekly-report-download');

    let historyChart;
    let mapInstance;
    let mapMarkers = [];

    function formatDateTime(value) {
        if (!value) {
            return '--';
        }
        return new Date(value).toLocaleString();
    }

    function setHistoryPlaceholder(message) {
        const existing = historyChartContainer.querySelector('.history-placeholder');
        if (existing) {
            existing.remove();
        }
        if (message) {
            const info = document.createElement('p');
            info.className = 'muted history-placeholder';
            info.textContent = message;
            historyChartContainer.appendChild(info);
        }
    }

    function populateRoads() {
        return fetch('/api/roads')
            .then(response => response.json())
            .then(data => {
                const selects = [roadSelect, historyRoadSelect].filter(Boolean);
                selects.forEach(select => {
                    select.innerHTML = '';
                    data.forEach(road => {
                        const option = document.createElement('option');
                        option.value = road.id;
                        option.textContent = `${road.name} (${road.code})`;
                        select.appendChild(option);
                    });
                });
                if (roadSelect && data.length && !roadSelect.value) {
                    roadSelect.value = data[0].id;
                }
                if (historyRoadSelect && data.length && !historyRoadSelect.value) {
                    historyRoadSelect.value = roadSelect ? roadSelect.value : data[0].id;
                }
                if (roadSelect && roadSelect.value) {
                    fetchRoadSnapshot(roadSelect.value);
                }
                if (historyForm && historyRoadSelect && historyRoadSelect.value) {
                    historyForm.dispatchEvent(new Event('submit'));
                }
            })
            .catch(error => console.error('Failed to load roads', error));
    }

    function fetchLatestTraffic() {
        fetch('/api/traffic/latest?limit=10')
            .then(response => response.json())
            .then(data => {
                trafficTbody.innerHTML = '';
                if (!data.length) {
                    trafficTbody.innerHTML = '<tr><td colspan="5">No traffic data available.</td></tr>';
                    return;
                }
                data.forEach(item => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${item.road_name ?? 'Unknown road'}</td>
                        <td>${formatDateTime(item.timestamp)}</td>
                        <td>${item.speed ?? '--'}</td>
                        <td>${item.volume ?? '--'}</td>
                        <td>${item.status ?? '--'}</td>
                    `;
                    trafficTbody.appendChild(row);
                });
            })
            .catch(error => console.error('Failed to load latest traffic', error));
    }

    function fetchActiveEvents() {
        fetch('/api/events?limit=10')
            .then(response => response.json())
            .then(data => {
                eventsTbody.innerHTML = '';
                if (!data.length) {
                    eventsTbody.innerHTML = '<tr><td colspan="4">No active events.</td></tr>';
                    return;
                }
                data.forEach(item => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${item.road_name ?? 'Unknown road'}</td>
                        <td>${item.type}</td>
                        <td>${item.description ?? '--'}</td>
                        <td>${formatDateTime(item.timestamp)}</td>
                    `;
                    eventsTbody.appendChild(row);
                });
                if (timelineList) {
                    timelineList.innerHTML = '';
                    data.slice(0, 5).forEach(item => {
                        const li = document.createElement('li');
                        li.innerHTML = `
                            <div class="timeline-dot"></div>
                            <div>
                                <div class="fw-semibold">${item.type} · ${item.road_name ?? 'Unknown'}</div>
                                <div class="muted small">${formatDateTime(item.timestamp)}</div>
                                <p class="mb-0">${item.description ?? 'No description provided.'}</p>
                            </div>
                        `;
                        timelineList.appendChild(li);
                    });
                }
            })
            .catch(error => console.error('Failed to load events', error));
    }

    function fetchRoadSnapshot(roadId) {
        if (!roadId) return;
        fetch(`/api/roads/${roadId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Road not found');
                }
                return response.json();
            })
            .then(data => {
                if (!data.road) return;
                roadDetailsName.textContent = `${data.road.name} (${data.road.code})`;
                roadDetailsMeta.textContent = `${data.road.length ?? '--'} km · ${data.road.lanes} lanes · Limit ${data.road.speed_limit ?? '--'} km/h`;
                roadDetailsLatest.textContent = data.latest?.speed
                    ? `${Number(data.latest.speed).toFixed(1)} km/h`
                    : '--';
                roadDetailsAvgSpeed.textContent = data.averages?.speed
                    ? `${Number(data.averages.speed).toFixed(1)} km/h`
                    : '--';
                roadDetailsAvgVolume.textContent = data.averages?.volume
                    ? `${Number(data.averages.volume).toFixed(0)}`
                    : '--';
                roadDetailsCongestion.textContent = data.averages?.congestion != null
                    ? `${Math.round(Number(data.averages.congestion) * 100)}%`
                    : '--';
                roadDetailsEvents.textContent = data.events_last_24h ?? '0';
            })
            .catch(error => console.error('Failed to load road snapshot', error));
    }

    function fetchSummary() {
        fetch('/api/dashboard/summary')
            .then(response => response.json())
            .then(data => {
                summaryTotalRoads.textContent = data.total_roads ?? '--';
                summaryActiveEvents.textContent = data.active_events ?? '--';
                summaryAvgSpeed.textContent = data.avg_speed_last_window
                    ? `${Number(data.avg_speed_last_window).toFixed(1)}`
                    : '--';
                summaryMaxVolume.textContent = data.max_volume_last_window ?? '--';
                summaryUpdatedAt.textContent = data.generated_at
                    ? `Updated at ${formatDateTime(data.generated_at)} (last ${data.window_hours}h)`
                    : '';

                summaryCongestedList.innerHTML = '';
                if (!data.top_congested_roads || !data.top_congested_roads.length) {
                    summaryCongestedList.innerHTML = '<li>No congestion in the last window.</li>';
                    return;
                }
                data.top_congested_roads.forEach(item => {
                    const li = document.createElement('li');
                    const percentage = item.avg_congestion != null
                        ? `${Math.round(item.avg_congestion * 100)}%`
                        : '--';
                    li.innerHTML = `<span>${item.road_name}</span><strong>${percentage}</strong>`;
                    summaryCongestedList.appendChild(li);
                });
            })
            .catch(error => console.error('Failed to load summary', error));
    }

    function buildHistoryAnnotations(eventData) {
        const annotations = {};
        eventData.forEach(event => {
            const label = formatDateTime(event.timestamp);
            annotations[`event-${event.id ?? label}`] = {
                type: 'line',
                scaleID: 'x',
                value: label,
                borderColor: 'rgba(220, 53, 69, 0.8)',
                borderWidth: 2,
                borderDash: [4, 4],
                label: {
                    enabled: false,
                },
            };
        });
        return annotations;
    }

    function fetchAlerts() {
        if (!alertCenter) return;
        fetch('/api/alerts')
            .then(response => response.json())
            .then(data => {
                alertCenter.innerHTML = '';
                const alerts = data.alerts || [];
                if (!alerts.length) {
                    alertCenter.innerHTML = '<div class="col-12 text-muted">No active alerts.</div>';
                    return;
                }
                    alerts.forEach(alert => {
                    const col = document.createElement('div');
                    col.className = 'col-md-6';
                    col.innerHTML = `
                        <div class="alert-card ${alert.level}">
                            <div class="fs-5">${alert.level === 'critical' ? '🚨' : '⚠️'}</div>
                            <div>
                                <div class="fw-semibold text-uppercase small">${alert.level}</div>
                                <p class="mb-0">${alert.message}</p>
                            </div>
                        </div>
                    `;
                    alertCenter.appendChild(col);
                });
            })
            .catch(error => console.error('Failed to load alerts', error));
    }

    function fetchSystemStatus() {
        if (!systemStatusList) return;
        fetch('/api/system/status')
            .then(response => response.json())
            .then(data => {
                systemStatusList.innerHTML = '';
                const totals = data.totals || {};
                Object.entries(totals).forEach(([key, value]) => {
                    const item = document.createElement('li');
                    item.className = 'list-group-item d-flex justify-content-between';
                    item.innerHTML = `<span class="text-capitalize">${key}</span><strong>${value}</strong>`;
                    systemStatusList.appendChild(item);
                });
                if (systemStatusUpdated) {
                    systemStatusUpdated.textContent = data.generated_at
                        ? `Updated ${formatDateTime(data.generated_at)}`
                        : '';
                }
            })
            .catch(error => console.error('Failed to load system status', error));
    }

    function initMap() {
        if (!mapView || typeof L === 'undefined') {
            return;
        }
        if (!mapInstance) {
            mapInstance = L.map('map-view').setView([30, 112], 4.5);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors',
            }).addTo(mapInstance);
        }
    }

    function updateMapMarkers() {
        if (!mapView) return;
        initMap();
        fetch('/api/events/map?limit=100')
            .then(response => response.json())
            .then(data => {
                if (!mapInstance) return;
                mapMarkers.forEach(marker => marker.remove());
                mapMarkers = [];
                data.forEach(event => {
                    if (!event.coordinates) return;
                    const marker = L.marker([event.coordinates.lat, event.coordinates.lon])
                        .addTo(mapInstance)
                        .bindPopup(`<strong>${event.type}</strong><br>${event.road_name ?? 'Unknown'}<br>${formatDateTime(event.timestamp)}`);
                    mapMarkers.push(marker);
                });
            })
            .catch(error => console.error('Failed to load map events', error));
    }

    function fetchWeeklyReport(download = false) {
        if (!weeklyReportCards) {
            if (download) {
                fetch('/api/reports/weekly')
                    .then(response => response.json())
                    .then(data => {
                        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                        const url = URL.createObjectURL(blob);
                        const link = document.createElement('a');
                        link.href = url;
                        link.download = 'weekly_report.json';
                        link.click();
                        URL.revokeObjectURL(url);
                    });
            }
            return;
        }
        fetch('/api/reports/weekly')
            .then(response => response.json())
            .then(data => {
                if (download) {
                    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = 'weekly_report.json';
                    link.click();
                    URL.revokeObjectURL(url);
                    return;
                }
                weeklyReportCards.innerHTML = '';
                const cards = [
                    {
                        title: 'Traffic Records (7d)',
                        value: data.traffic_records ?? '--',
                        desc: 'Total samples ingested',
                    },
                    {
                        title: 'Avg Speed',
                        value: data.avg_speed ? `${Number(data.avg_speed).toFixed(1)} km/h` : '--',
                        desc: 'Across all roads',
                    },
                    {
                        title: 'Events',
                        value: data.events ? `${data.events.total} total / ${data.events.severe} severe` : '--',
                        desc: 'Created last 7 days',
                    },
                ];
                cards.forEach(card => {
                    const col = document.createElement('div');
                    col.className = 'col-md-4';
                    col.innerHTML = `
                        <div class="p-3 bg-light rounded-3 h-100">
                            <h6>${card.title}</h6>
                            <div class="display-6">${card.value}</div>
                            <p class="muted mb-0">${card.desc}</p>
                        </div>
                    `;
                    weeklyReportCards.appendChild(col);
                });

                const roads = document.createElement('div');
                roads.className = 'col-md-12';
                const listItems = (data.busiest_roads || [])
                    .map(
                        item =>
                            `<li class="road-stat"><span>${item.road_name}</span><strong>${item.avg_volume ? Number(item.avg_volume).toFixed(0) : '--'}</strong></li>`
                    )
                    .join('');
                roads.innerHTML = `
                    <div class="p-3 bg-white rounded-3 h-100">
                        <h6>Busiest Roads</h6>
                        <div>${listItems || '<div class="muted">No data.</div>'}</div>
                    </div>
                `;
                weeklyReportCards.appendChild(roads);
            })
            .catch(error => console.error('Failed to load weekly report', error));
    }

    historyForm.addEventListener('submit', event => {
        event.preventDefault();
        const roadId = historyRoadSelect ? historyRoadSelect.value : roadSelect.value;
        const startTime = document.getElementById('start-time').value;
        const endTime = document.getElementById('end-time').value;

        let url = `/api/traffic/history/${roadId}`;
        const params = new URLSearchParams();
        if (startTime) params.append('start', new Date(startTime).toISOString());
        if (endTime) params.append('end', new Date(endTime).toISOString());
        if (params.toString()) url += `?${params.toString()}`;

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load history data');
                }
                return response.json();
            })
            .then(data => {
                if (historyChart) {
                    historyChart.destroy();
                }

                const trafficData = data.traffic || [];
                const eventData = data.events || [];

                historyWindowInfo.textContent = data.window
                    ? `Showing data from ${formatDateTime(data.window.start)} to ${formatDateTime(data.window.end)}`
                    : '';

                historyEventsTbody.innerHTML = '';
                if (!eventData.length) {
                    historyEventsTbody.innerHTML = '<tr><td colspan="3">No events in this window.</td></tr>';
                } else {
                    eventData.forEach(item => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${formatDateTime(item.timestamp)}</td>
                            <td>${item.type}</td>
                            <td>${item.description ?? '--'}</td>
                        `;
                        historyEventsTbody.appendChild(row);
                    });
                }

                setHistoryPlaceholder('');
                historyChart = new Chart(historyChartCtx, {
                    type: 'line',
                    data: {
                        labels: trafficData.map(d => formatDateTime(d.timestamp)),
                        datasets: [
                            {
                                label: 'Speed (km/h)',
                                data: trafficData.map(d => d.speed ?? 0),
                                borderColor: 'rgba(75, 192, 192, 1)',
                                yAxisID: 'y-speed',
                                tension: 0.1,
                                fill: false,
                            },
                            {
                                label: 'Volume',
                                data: trafficData.map(d => d.volume ?? 0),
                                borderColor: 'rgba(255, 99, 132, 1)',
                                yAxisID: 'y-volume',
                                tension: 0.1,
                                fill: false,
                            },
                        ],
                    },
                    options: {
                        interaction: {
                            intersect: false,
                            mode: 'index',
                        },
                        scales: {
                            'y-speed': {
                                type: 'linear',
                                position: 'left',
                                title: {
                                    display: true,
                                    text: 'Speed (km/h)',
                                },
                            },
                            'y-volume': {
                                type: 'linear',
                                position: 'right',
                                title: {
                                    display: true,
                                    text: 'Volume',
                                },
                                grid: {
                                    drawOnChartArea: false,
                                },
                            },
                        },
                        plugins: {
                            annotation: {
                                annotations: buildHistoryAnnotations(eventData),
                            },
                        },
                    },
                });

                if (!trafficData.length) {
                    setHistoryPlaceholder('No traffic data for the selected window.');
                }
            })
            .catch(error => {
                historyEventsTbody.innerHTML = '<tr><td colspan="3">Unable to load history data.</td></tr>';
                setHistoryPlaceholder('Unable to load traffic history.');
                console.error(error);
            });
    });

    function refreshRealtimeData() {
        fetchLatestTraffic();
        fetchActiveEvents();
        fetchSummary();
        fetchAlerts();
        fetchSystemStatus();
        updateMapMarkers();
    }

    if (roadSelect) {
        roadSelect.addEventListener('change', () => {
            fetchRoadSnapshot(roadSelect.value);
        });
    }

    if (historyRoadSelect) {
        historyRoadSelect.addEventListener('change', () => {
            historyForm.dispatchEvent(new Event('submit'));
        });
    }

    if (weeklyDownloadButton) {
        weeklyDownloadButton.addEventListener('click', () => fetchWeeklyReport(true));
    }

    populateRoads();
    refreshRealtimeData();
    fetchWeeklyReport();
    setInterval(refreshRealtimeData, 30000);
    setInterval(fetchWeeklyReport, 5 * 60 * 1000);
});
