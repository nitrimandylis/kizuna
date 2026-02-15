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
    
    // Calendar - always renders 6 rows (42 cells) for consistent height
    const calendarDays = document.getElementById('calendarDays');
    const calendarTitle = document.getElementById('calendarTitle');
    const prevBtn = document.getElementById('prevMonth');
    const nextBtn = document.getElementById('nextMonth');
    
    if (calendarDays && calendarTitle) {
        let currentDate = new Date();
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December'];
        
        function renderCalendar(date) {
            const year = date.getFullYear();
            const month = date.getMonth();
            
            calendarTitle.textContent = monthNames[month] + ' ' + year;
            
            const firstDay = new Date(year, month, 1);
            const lastDay = new Date(year, month + 1, 0);
            const startDay = firstDay.getDay();
            const daysInMonth = lastDay.getDate();
            const daysInPrevMonth = new Date(year, month, 0).getDate();
            
            const today = new Date();
            const todayStr = today.toDateString();
            
            // Always render 42 cells (6 rows x 7 days) for consistent height
            const totalCells = 42;
            
            let html = '';
            let dayCount = 1;
            let nextMonthDay = 1;
            
            for (let i = 0; i < totalCells; i++) {
                let dayNumber;
                let isOtherMonth = false;
                let isToday = false;
                
                if (i < startDay) {
                    // Previous month days
                    dayNumber = daysInPrevMonth - startDay + i + 1;
                    isOtherMonth = true;
                } else if (dayCount > daysInMonth) {
                    // Next month days
                    dayNumber = nextMonthDay;
                    nextMonthDay++;
                    isOtherMonth = true;
                } else {
                    // Current month days
                    dayNumber = dayCount;
                    const cellDate = new Date(year, month, dayCount);
                    if (cellDate.toDateString() === todayStr) {
                        isToday = true;
                    }
                    dayCount++;
                }
                
                const classes = ['calendar-day'];
                if (isOtherMonth) classes.push('other-month');
                if (isToday) classes.push('today');
                
                const dateStr = year + '-' + String(month + 1).padStart(2, '0') + '-' + String(dayNumber).padStart(2, '0');
                
                html += '<div class="' + classes.join(' ') + '" data-date="' + dateStr + '">';
                html += '<span class="calendar-day-number">' + dayNumber + '</span>';
                html += '<div class="calendar-event-dots"></div>';
                html += '</div>';
            }
            
            calendarDays.innerHTML = html;
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', function() {
                currentDate.setMonth(currentDate.getMonth() - 1);
                renderCalendar(currentDate);
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', function() {
                currentDate.setMonth(currentDate.getMonth() + 1);
                renderCalendar(currentDate);
            });
        }
        
        renderCalendar(currentDate);
    }
});
