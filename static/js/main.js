document.addEventListener('DOMContentLoaded', function() {
    // Skip link focus management
    const skipLink = document.querySelector('.skip-link');
    const mainContent = document.getElementById('main-content');
    
    if (skipLink && mainContent) {
        skipLink.addEventListener('click', function(e) {
            e.preventDefault();
            mainContent.focus();
        });
    }
    
    // Mobile navigation toggle with accessibility
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            const isOpen = navMenu.classList.toggle('active');
            navToggle.setAttribute('aria-expanded', isOpen);
        });
        
        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
                navToggle.setAttribute('aria-expanded', 'false');
                navToggle.focus();
            }
        });
    }
    
    // Set active nav link based on current page
    const navLinks = document.querySelectorAll('.nav-link');
    const currentPath = window.location.pathname;
    
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        }
    });
    
    // Enhanced alert handling with close buttons
    const alertContainer = document.querySelector('.alert-container');
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(function(alert) {
        const closeBtn = alert.querySelector('.alert-close');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(function() {
                    alert.remove();
                    if (alertContainer && alertContainer.children.length === 0) {
                        alertContainer.remove();
                    }
                }, 300);
            });
        }
        
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            if (alert && alert.parentNode) {
                alert.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(function() {
                    if (alert.parentNode) {
                        alert.remove();
                        if (alertContainer && alertContainer.children.length === 0) {
                            alertContainer.remove();
                        }
                    }
                }, 300);
            }
        }, 5000);
    });
    
    // Loading state for forms
    const forms = document.querySelectorAll('form[data-loading]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.classList.contains('btn-loading')) {
                submitBtn.classList.add('btn-loading');
                submitBtn.disabled = true;
                submitBtn.dataset.originalText = submitBtn.textContent;
                submitBtn.textContent = 'Loading...';
            }
        });
    });
    
    // Loading state for buttons with data-loading attribute
    const loadingBtns = document.querySelectorAll('.btn[data-loading="true"]');
    loadingBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            if (!btn.classList.contains('btn-loading')) {
                btn.classList.add('btn-loading');
                btn.disabled = true;
                btn.dataset.originalText = btn.textContent;
                btn.innerHTML = '<span class="spinner"></span> Loading...';
            }
        });
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
                
                const eventCount = eventsByDate[dateStr] ? eventsByDate[dateStr].length : 0;
                
                html += '<div class="' + classes.join(' ') + '" data-date="' + dateStr + '" tabindex="0" role="button" aria-label="' + (dateStr ? new Date(dateStr).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }) : '') + (eventCount ? ', ' + eventCount + ' event' + (eventCount > 1 ? 's' : '') : '') + '">';
                html += '<div class="calendar-day-header">';
                html += '<span class="calendar-day-number">' + dayNumber + '</span>';
                if (eventCount > 0) {
                    html += '<span class="event-count" aria-hidden="true">' + eventCount + '</span>';
                }
                html += '</div>';
                html += '<div class="calendar-day-content">';
                
                // Add events for this date (max 3 visible)
                if (dateStr && eventsByDate[dateStr]) {
                    const visibleEvents = eventsByDate[dateStr].slice(0, 3);
                    visibleEvents.forEach(function(event) {
                        html += '<div class="calendar-event cas-' + event.cas_type + '" title="' + event.title + '">';
                        html += event.title;
                        html += '</div>';
                    });
                    if (eventsByDate[dateStr].length > 3) {
                        html += '<div class="calendar-more">+' + (eventsByDate[dateStr].length - 3) + ' more</div>';
                    }
                }
                
                html += '</div>';
                html += '</div>';
            }
            
            calendarDays.innerHTML = html;
        }
        
        function fetchEvents(year, month) {
            // Show loading state
            if (calendarDays) {
                calendarDays.style.opacity = '0.5';
            }
            
            fetch('/api/events?year=' + year + '&month=' + month)
                .then(function(response) {
                    return response.json();
                })
                .then(function(events) {
                    renderCalendar(currentDate, events);
                    if (calendarDays) {
                        calendarDays.style.opacity = '1';
                    }
                })
                .catch(function(error) {
                    console.error('Error fetching events:', error);
                    renderCalendar(currentDate, []);
                    if (calendarDays) {
                        calendarDays.style.opacity = '1';
                    }
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
        
        // Keyboard navigation for calendar
        document.addEventListener('keydown', function(e) {
            if (document.activeElement && document.activeElement.classList.contains('calendar-day')) {
                if (e.key === 'ArrowLeft') {
                    currentDate.setMonth(currentDate.getMonth() - 1);
                    loadCalendar();
                } else if (e.key === 'ArrowRight') {
                    currentDate.setMonth(currentDate.getMonth() + 1);
                    loadCalendar();
                }
            }
        });
        
        // Initial load
        loadCalendar();
    }
    
    // Search input debounce
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(function(input) {
        let debounceTimer;
        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            const form = input.closest('form');
            if (form && input.value.length >= 2) {
                // Add visual feedback
                input.classList.add('searching');
            } else {
                input.classList.remove('searching');
            }
        });
    });
    
    // User dropdown toggle
    const userDropdown = document.querySelector('.user-dropdown');
    const userAvatar = document.querySelector('.user-avatar');
    
    if (userDropdown && userAvatar) {
        userAvatar.addEventListener('click', function(e) {
            e.stopPropagation();
            const isOpen = userDropdown.classList.toggle('active');
            userAvatar.setAttribute('aria-expanded', isOpen);
        });
        
        // Close dropdown on outside click
        document.addEventListener('click', function(e) {
            if (userDropdown.classList.contains('active') && !userDropdown.contains(e.target)) {
                userDropdown.classList.remove('active');
                userAvatar.setAttribute('aria-expanded', 'false');
            }
        });
        
        // Close dropdown on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && userDropdown.classList.contains('active')) {
                userDropdown.classList.remove('active');
                userAvatar.setAttribute('aria-expanded', 'false');
                userAvatar.focus();
            }
        });
    }
});

// Helper function to reset button state
function resetButtonState(btn) {
    if (btn && btn.dataset.originalText) {
        btn.textContent = btn.dataset.originalText;
        btn.classList.remove('btn-loading');
        btn.disabled = false;
    }
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = '@keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }';
document.head.appendChild(style);
