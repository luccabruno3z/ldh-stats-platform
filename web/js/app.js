/* ============================================
   Legión de Hierro - Main Application JS
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    const playerNameInput = document.getElementById('player-name');
    const suggestionsContainer = document.getElementById('suggestions');
    const performanceHistoryChart = document.getElementById('performanceHistoryChart');
    let playersData = [];
    let playersDataLoaded = false;
    let playersDataLoading = false;

    // Chart instance reference to prevent memory leaks
    let performanceChartInstance = null;
    let clanAveragesChartInstance = null;

    // ============================================
    // Lazy load player data
    // ============================================
    function loadPlayersData() {
        if (playersDataLoaded || playersDataLoading) return Promise.resolve(playersData);
        playersDataLoading = true;

        return fetch('https://luccabruno3z.github.io/graphs/all_players_clusters.json')
            .then(response => {
                if (!response.ok) throw new Error('Error al cargar datos de jugadores');
                return response.json();
            })
            .then(data => {
                playersData = data;
                playersData.sort((a, b) => b["Performance Score"] - a["Performance Score"]);
                playersDataLoaded = true;
                playersDataLoading = false;
                return playersData;
            })
            .catch(error => {
                playersDataLoading = false;
                console.error('Error al cargar el archivo JSON:', error);
                showError('Error al cargar datos de jugadores. Intenta recargar la página.');
                return [];
            });
    }

    // Use requestIdleCallback to preload if available, otherwise defer
    if ('requestIdleCallback' in window) {
        requestIdleCallback(function() {
            loadPlayersData();
        });
    }

    // Also load on first focus of any search input
    function onSearchInputFocus() {
        loadPlayersData();
    }

    playerNameInput.addEventListener('focus', onSearchInputFocus, { once: true });

    // ============================================
    // Error display helper
    // ============================================
    function showError(message, container) {
        const target = container || document.getElementById('search-results');
        target.innerHTML = `<p class="error">${message}</p>`;
    }

    // ============================================
    // Suggestion system with keyboard navigation and ARIA
    // ============================================
    function createSuggestions(input, container, onSelect) {
        let activeIndex = -1;

        function updateSuggestions() {
            const query = input.value.trim().toLowerCase();
            container.innerHTML = '';
            activeIndex = -1;

            if (query.length === 0 || !playersDataLoaded) return;

            const filteredPlayers = playersData.filter(player =>
                player.Player.toLowerCase().includes(query)
            ).slice(0, 50); // Limit to 50 suggestions for performance

            filteredPlayers.forEach((player, index) => {
                const suggestionItem = document.createElement('div');
                suggestionItem.classList.add('suggestion-item');
                suggestionItem.textContent = player.Player;
                suggestionItem.setAttribute('role', 'option');
                suggestionItem.setAttribute('aria-selected', 'false');
                suggestionItem.setAttribute('id', container.id + '-option-' + index);
                suggestionItem.addEventListener('click', function() {
                    input.value = player.Player;
                    container.innerHTML = '';
                    activeIndex = -1;
                    if (onSelect) onSelect(player);
                });
                container.appendChild(suggestionItem);
            });
        }

        function handleKeydown(e) {
            const items = container.querySelectorAll('.suggestion-item');
            if (items.length === 0) return;

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                activeIndex = Math.min(activeIndex + 1, items.length - 1);
                updateActiveItem(items);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                activeIndex = Math.max(activeIndex - 1, 0);
                updateActiveItem(items);
            } else if (e.key === 'Enter' && activeIndex >= 0) {
                e.preventDefault();
                items[activeIndex].click();
            } else if (e.key === 'Escape') {
                container.innerHTML = '';
                activeIndex = -1;
            }
        }

        function updateActiveItem(items) {
            items.forEach((item, i) => {
                item.setAttribute('aria-selected', i === activeIndex ? 'true' : 'false');
            });
            if (activeIndex >= 0 && items[activeIndex]) {
                items[activeIndex].scrollIntoView({ block: 'nearest' });
                input.setAttribute('aria-activedescendant', items[activeIndex].id);
            }
        }

        input.addEventListener('input', function() {
            if (!playersDataLoaded) {
                loadPlayersData().then(updateSuggestions);
            } else {
                updateSuggestions();
            }
        });

        input.addEventListener('keydown', handleKeydown);

        // Load data on focus for team inputs too
        input.addEventListener('focus', function() {
            if (!playersDataLoaded && !playersDataLoading) {
                loadPlayersData();
            }
        }, { once: true });
    }

    // ============================================
    // Close all suggestion dropdowns when clicking outside
    // ============================================
    document.addEventListener('click', function(e) {
        const allSuggestions = document.querySelectorAll('.suggestions');
        allSuggestions.forEach(function(container) {
            // Check if the click is outside the container and its associated input
            const parentForm = container.closest('form') || container.parentElement;
            if (!parentForm.contains(e.target)) {
                container.innerHTML = '';
            }
        });
    });

    // ============================================
    // Player search suggestions
    // ============================================
    createSuggestions(playerNameInput, suggestionsContainer);

    // ============================================
    // Player search form submission
    // ============================================
    document.getElementById('search-form').addEventListener('submit', function(event) {
        event.preventDefault();

        if (!playersDataLoaded) {
            loadPlayersData().then(function() {
                performSearch();
            });
            return;
        }
        performSearch();
    });

    function performSearch() {
        const playerName = playerNameInput.value.trim();
        const player = playersData.find(p => p.Player.toLowerCase() === playerName.toLowerCase());
        const resultsContainer = document.getElementById('search-results');
        resultsContainer.innerHTML = '';

        if (player) {
            const ranking = playersData.findIndex(p => p.Player.toLowerCase() === playerName.toLowerCase()) + 1;
            const clanLogo = `<img src="logos/Logo_${player.Clan}.png" alt="Logo ${player.Clan}" class="clan-logo" onerror="this.onerror=null;this.src='logos/Logo_${player.Clan}.gif';">`;
            const playerStats = `
                <div class="stats-box">
                    ${clanLogo}
                    <h3>Estadísticas de ${player.Player}</h3>
                    <p><strong>Ranking Global:</strong> #${ranking}</p>
                    <p><strong>Clan:</strong> ${player.Clan}</p>
                    <p><strong>Puntuación Total:</strong> ${player["Total Score"]}</p>
                    <p><strong>Muertes Totales:</strong> ${player["Total Deaths"]}</p>
                    <p><strong>Asesinatos Totales:</strong> ${player["Total Kills"]}</p>
                    <p><strong>Rondas Jugadas:</strong> ${player.Rounds}</p>
                    <p><strong>K/D Ratio:</strong> ${player["K/D Ratio"].toFixed(2)}</p>
                    <p><strong>Puntos por Ronda:</strong> ${player["Score per Round"].toFixed(2)}</p>
                    <p><strong>Asesinatos por Ronda:</strong> ${player["Kills per Round"].toFixed(2)}</p>
                    <p><strong>Performance Score:</strong> ${player["Performance Score"].toFixed(2)}</p>
                </div>
            `;
            resultsContainer.innerHTML = playerStats;

            // Buscar y mostrar historial del jugador
            buscarHistorialJugador(playerName)
                .then(historyData => {
                    if (historyData) {
                        mostrarHistorialPerformance(historyData);
                    }
                })
                .catch(error => console.error('Error al cargar el historial de performance:', error));
        } else {
            resultsContainer.innerHTML = '<p class="error">Jugador no encontrado.</p>';
        }
    }

    // ============================================
    // Player history functions
    // ============================================
    function buscarHistorialJugador(nombreJugador) {
        const nombreNormalizado = normalizarNombre(nombreJugador);
        const url = `https://luccabruno3z.github.io/graphs/history/${nombreNormalizado}_history.json`;

        return fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Historial no encontrado');
                }
                return response.json();
            })
            .catch(error => {
                console.error('Error al cargar el archivo JSON:', error);
                return null;
            });
    }

    function normalizarNombre(nombre) {
        return nombre.replace(/[^a-zA-Z0-9_-]/g, '_');
    }

    // FIX: Chart.js memory leak - destroy existing chart before creating new one
    function mostrarHistorialPerformance(historyData) {
        const dates = historyData.map(entry => entry.Date);
        const scores = historyData.map(entry => entry["Performance Score"]);

        performanceHistoryChart.style.display = 'block';

        // Destroy previous chart instance to prevent memory leak
        if (performanceChartInstance) {
            performanceChartInstance.destroy();
            performanceChartInstance = null;
        }

        performanceChartInstance = new Chart(performanceHistoryChart, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Performance Score',
                    data: scores,
                    borderColor: 'rgba(0, 255, 255, 0.8)',
                    backgroundColor: 'rgba(0, 255, 255, 0.2)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#fff'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#fff'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    // ============================================
    // Clan averages chart and stats
    // ============================================
    fetch('https://luccabruno3z.github.io/graphs/clan_averages.json')
        .then(response => {
            if (!response.ok) throw new Error('Error al cargar promedios de clanes');
            return response.json();
        })
        .then(data => {
            const averagesContainer = document.getElementById('clan-averages-results');
            averagesContainer.innerHTML = '';

            const clanNames = data.map(clan => clan.Clan);
            const performanceScores = data.map(clan => clan["Performance Score"]);

            const ctx = document.getElementById('clanAveragesChart').getContext('2d');

            // Destroy previous chart instance if any
            if (clanAveragesChartInstance) {
                clanAveragesChartInstance.destroy();
                clanAveragesChartInstance = null;
            }

            clanAveragesChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: clanNames,
                    datasets: [{
                        label: 'Performance Score',
                        data: performanceScores,
                        backgroundColor: 'rgba(0, 255, 255, 0.5)',
                        borderColor: 'rgba(0, 255, 255, 0.8)',
                        borderWidth: 1,
                        hoverBackgroundColor: 'rgba(0, 255, 255, 0.8)',
                        hoverBorderColor: 'rgba(0, 255, 255, 1)',
                        borderRadius: 5,
                        barThickness: 30,
                        shadowOffsetX: 3,
                        shadowOffsetY: 3,
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 255, 255, 0.5)',
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: '#fff'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: '#fff'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });

            data.forEach(clan => {
                const clanAverage = `
                    <div class="stats-box">
                        <h3>${clan.Clan}</h3>
                        <p><strong>Promedio K/D:</strong> ${clan["K/D Ratio"].toFixed(2)}</p>
                        <p><strong>Promedio Score:</strong> ${clan["Score per Round"].toFixed(2)}</p>
                        <p><strong>Promedio Kills:</strong> ${clan["Kills per Round"].toFixed(2)}</p>
                        <p><strong>Performance Score:</strong> ${clan["Performance Score"].toFixed(2)}</p>
                    </div>
                `;
                averagesContainer.innerHTML += clanAverage;
            });
        })
        .catch(error => {
            console.error('Error al cargar el archivo JSON de promedios:', error);
            showError('Error al cargar promedios de clanes.', document.getElementById('clan-averages-results'));
        });

    // ============================================
    // Team analysis - suggestions for player inputs
    // ============================================
    const teamInputs = [
        document.getElementById('player1'),
        document.getElementById('player2'),
        document.getElementById('player3'),
        document.getElementById('player4'),
        document.getElementById('player5'),
        document.getElementById('player6'),
        document.getElementById('player7'),
        document.getElementById('player8')
    ];

    const suggestionContainers = [
        document.getElementById('suggestions1'),
        document.getElementById('suggestions2'),
        document.getElementById('suggestions3'),
        document.getElementById('suggestions4'),
        document.getElementById('suggestions5'),
        document.getElementById('suggestions6'),
        document.getElementById('suggestions7'),
        document.getElementById('suggestions8')
    ];

    teamInputs.forEach((input, index) => {
        createSuggestions(input, suggestionContainers[index]);
    });

    // ============================================
    // Team analysis form submission
    // ============================================
    const teamForm = document.getElementById('team-analysis-form');
    const teamResultsContainer = document.getElementById('team-analysis-results');

    teamForm.addEventListener('submit', function(event) {
        event.preventDefault();

        if (!playersDataLoaded) {
            loadPlayersData().then(function() {
                analyzeTeam();
            });
            return;
        }
        analyzeTeam();
    });

    function analyzeTeam() {
        const playerInputValues = teamInputs.map(input => input.value.trim()).filter(name => name);

        if (playerInputValues.length < 2 || playerInputValues.length > 8) {
            teamResultsContainer.innerHTML = '<p class="error">Por favor, selecciona entre 2 y 8 jugadores.</p>';
            return;
        }

        let equipo;
        try {
            equipo = playerInputValues.map(name => {
                const jugador = playersData.find(p => p.Player.toLowerCase() === name.toLowerCase());
                if (!jugador) {
                    throw new Error(`Jugador '${name}' no encontrado en la base de datos.`);
                }
                return jugador;
            });
        } catch (error) {
            teamResultsContainer.innerHTML = `<p class="error">${error.message}</p>`;
            return;
        }

        const total_score = equipo.reduce((acc, jugador) => acc + jugador['Total Score'], 0);
        const total_kills = equipo.reduce((acc, jugador) => acc + jugador['Total Kills'], 0);
        const total_deaths = equipo.reduce((acc, jugador) => acc + jugador['Total Deaths'], 0);
        const total_rounds = equipo.reduce((acc, jugador) => acc + jugador['Rounds'], 0);
        const total_performance_score = equipo.reduce((acc, jugador) => acc + jugador['Performance Score'], 0) / equipo.length;
        const avg_kills_per_round = total_kills / total_rounds || 0;
        const avg_deaths_per_round = total_deaths / total_rounds || 0;
        const team_kd_ratio = total_kills / total_deaths || 0;

        let resultsHTML = '<div class="stats-box"><h3>Métricas del Equipo</h3>';
        resultsHTML += `<p><strong>Total Score:</strong> ${total_score}</p>`;
        resultsHTML += `<p><strong>Total Kills:</strong> ${total_kills}</p>`;
        resultsHTML += `<p><strong>Total Deaths:</strong> ${total_deaths}</p>`;
        resultsHTML += `<p><strong>Total Rounds:</strong> ${total_rounds}</p>`;
        resultsHTML += `<p><strong>Average Kills per Round:</strong> ${avg_kills_per_round.toFixed(2)}</p>`;
        resultsHTML += `<p><strong>Average Deaths per Round:</strong> ${avg_deaths_per_round.toFixed(2)}</p>`;
        resultsHTML += `<p><strong>Team K/D Ratio:</strong> ${team_kd_ratio.toFixed(2)}</p>`;
        resultsHTML += `<p><strong>Average Performance Score:</strong> ${total_performance_score.toFixed(2)}</p></div>`;

        equipo.forEach(jugador => {
            const clanLogo = `<img src="logos/Logo_${jugador.Clan}.png" alt="Logo ${jugador.Clan}" class="clan-logo" onerror="this.onerror=null;this.src='logos/Logo_${jugador.Clan}.gif';">`;
            resultsHTML += `<div class="stats-box"><h3>${jugador.Player}</h3>`;
            resultsHTML += `${clanLogo}`;
            resultsHTML += `<p><strong>Clan:</strong> ${jugador.Clan}</p>`;
            resultsHTML += `<p><strong>K/D Ratio:</strong> ${jugador['K/D Ratio'].toFixed(2)}</p>`;
            resultsHTML += `<p><strong>Total Kills:</strong> ${jugador['Total Kills']}</p>`;
            resultsHTML += `<p><strong>Total Deaths:</strong> ${jugador['Total Deaths']}</p>`;
            resultsHTML += `<p><strong>Rounds Jugados:</strong> ${jugador['Rounds']}</p>`;
            resultsHTML += `<p><strong>Performance Score:</strong> ${jugador['Performance Score'].toFixed(2)}</p></div>`;
        });

        teamResultsContainer.innerHTML = resultsHTML;
    }
});
