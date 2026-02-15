document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.3s';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });
    
    // Calendar functionality
    const calendarDays = document.getElementById('calendarDays');
    const calendarTitle = document.getElementById('calendarTitle');
    const prevBtn = document.getElementById('prevMonth');
    const nextBtn = document.getElementById('nextMonth');
    
    if (calendarDays && calendarTitle) {
        let currentDate = new Date();
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December'];
        
        function renderCalendar(date, events) {
            const year = date.getFullYear();
            const month = date.getMonth();
            
            calendarTitle.textContent = monthNames[month] + ' ' + year;
            
            const firstDay = new Date(year, month, 1);
            const lastDay = new Date(year, month + 1, 0);
            const startDay = firstDay.getDay();
            const daysInMonth = lastDay.getDate();
            const daysInPrevMonth = new Date(year, month, 0).getDate();
            
            const today = new Date();
            const todayStr = today.getFullYear() + '-' + 
                            String(today.getMonth() + 1).padStart(2, '0') + '-' + 
                            String(today.getDate()).padStart(2, '0');
            
            // Group events by date
            const eventsByDate = {};
            if (events) {
                events.forEach(function(event) {
                    if (!eventsByDate[event.date]) {
                        eventsByDate[event.date] = [];
                    }
                    eventsByDate[event.date].push(event);
                });
            }
            
            // Always render 42 cells (6 rows x 7 days) for consistent height
            const totalCells = 42;
            
            let html = '';
            let dayCount = 1;
            let nextMonthDay = 1;
            
            for (let i = 0; i < totalCells; i++) {
                let dayNumber;
                let isOtherMonth = false;
                let isToday = false;
                let dateStr = '';
                
                if (i < startDay) {
                    dayNumber = daysInPrevMonth - startDay + i + 1;
                    isOtherMonth = true;
                } else if (dayCount > daysInMonth) {
                    dayNumber = nextMonthDay;
                    nextMonthDay++;
                    isOtherMonth = true;
                } else {
                    dayNumber = dayCount;
                    const m = String(month + 1).padStart(2, '0');
                    const d = String(dayCount).padStart(2, '0');
                    dateStr = year + '-' + m + '-' + d;
                    
                    if (dateStr === todayStr) {
                        isToday = true;
                    }
                    dayCount++;
                }
                
                const classes = ['calendar-day'];
                if (isOtherMonth) classes.push('other-month');
                if (isToday) classes.push('today');
                
                html += '<div class="' + classes.join(' ') + '" data-date="' + dateStr + '">';
                html += '<div class="calendar-day-header">';
                html += '<span class="calendar-day-number">' + dayNumber + '</span>';
                html += '</div>';
                html += '<div class="calendar-day-content">';
                
                // Add events for this date
                if (dateStr && eventsByDate[dateStr]) {
                    eventsByDate[dateStr].forEach(function(event) {
                        html += '<div class="calendar-event cas-' + event.cas_type + '" title="' + event.title + '">';
                        html += event.title;
                        html += '</div>';
                    });
                }
                
                html += '</div>';
                html += '</div>';
            }
            
            calendarDays.innerHTML = html;
        }
        
        function fetchEvents(year, month) {
            fetch('/api/events?year=' + year + '&month=' + month)
                .then(function(response) {
                    return response.json();
                })
                .then(function(events) {
                    renderCalendar(currentDate, events);
                })
                .catch(function(error) {
                    console.error('Error fetching events:', error);
                    renderCalendar(currentDate, []);
                });
        }
        
        function loadCalendar() {
            const year = currentDate.getFullYear();
            const month = currentDate.getMonth() + 1;
            fetchEvents(year, month);
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', function() {
                currentDate.setMonth(currentDate.getMonth() - 1);
                loadCalendar();
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', function() {
                currentDate.setMonth(currentDate.getMonth() + 1);
                loadCalendar();
            });
        }
        
        // Initial load
        loadCalendar();
    }
});
