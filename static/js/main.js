// Smart India Hackathon 2025 - PM Internship Matching System
// Interactive JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive components
    initializeSkillsInput();
    initializeInterestsInput();
    initializeMatchingInterface();
    initializeProgressBars();
    initializeTooltips();
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        });
    }, 5000);
});

// Skills and Interests Multi-Select Functionality
function initializeSkillsInput() {
    const skillsContainer = document.getElementById('skills-container');
    if (!skillsContainer) return;
    
    const predefinedSkills = [
        'Python', 'JavaScript', 'Java', 'Data Analysis', 'Machine Learning',
        'Digital Marketing', 'Content Writing', 'Project Management',
        'Research', 'Communication', 'Leadership', 'Problem Solving',
        'Excel', 'SQL', 'Web Development', 'Mobile Development',
        'Cybersecurity', 'Network Security', 'Cloud Computing',
        'Artificial Intelligence', 'Data Science', 'Statistics',
        'Financial Analysis', 'Economics', 'Healthcare', 'Education',
        'Environmental Science', 'Policy Research', 'Documentation',
        'GIS', 'Social Media', 'Analytics', 'Community Engagement',
        'Medical Research', 'Learning Design', 'Ethical Hacking'
    ];
    
    createMultiSelectInterface(skillsContainer, predefinedSkills, 'skills', 'Select your skills');
}

function initializeInterestsInput() {
    const interestsContainer = document.getElementById('interests-container');
    if (!interestsContainer) return;
    
    const predefinedInterests = [
        'Technology', 'Healthcare', 'Education', 'Finance & Banking',
        'Rural Development', 'Environment', 'Research & Analytics',
        'Cybersecurity', 'Digital Marketing', 'Data Science',
        'Policy Development', 'Community Service', 'Innovation',
        'Entrepreneurship', 'Social Impact', 'Government Services',
        'Public Administration', 'Economic Development'
    ];
    
    createMultiSelectInterface(interestsContainer, predefinedInterests, 'interests', 'Select your interests');
}

function createMultiSelectInterface(container, options, fieldName, placeholder) {
    const selectedItems = new Set();
    
    // Create the interface HTML
    container.innerHTML = `
        <div class="multi-select-wrapper">
            <div class="selected-items" id="${fieldName}-selected"></div>
            <div class="dropdown">
                <input type="text" class="form-control dropdown-input" 
                       placeholder="${placeholder}" id="${fieldName}-input" autocomplete="off">
                <div class="dropdown-menu" id="${fieldName}-dropdown" style="display: none;">
                    ${options.map(option => `
                        <div class="dropdown-item" data-value="${option}">
                            <i class="fas fa-plus"></i> ${option}
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
        <style>
            .multi-select-wrapper {
                position: relative;
                margin-bottom: 1rem;
            }
            .selected-items {
                min-height: 40px;
                margin-bottom: 0.5rem;
                padding: 0.5rem;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                background-color: var(--bg-card);
            }
            .selected-item {
                display: inline-block;
                background-color: var(--color-primary);
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-size: 0.875rem;
                margin: 0.25rem;
                font-weight: 500;
            }
            .selected-item .remove-btn {
                margin-left: 0.5rem;
                cursor: pointer;
                font-weight: bold;
            }
            .dropdown {
                position: relative;
            }
            .dropdown-menu {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background-color: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                max-height: 200px;
                overflow-y: auto;
                z-index: 1000;
                box-shadow: var(--shadow-lg);
            }
            .dropdown-item {
                padding: 0.75rem 1rem;
                cursor: pointer;
                border-bottom: 1px solid var(--border-color);
                color: var(--color-text);
                transition: background-color 0.2s ease;
            }
            .dropdown-item:hover {
                background-color: var(--color-primary);
                color: white;
            }
            .dropdown-item:last-child {
                border-bottom: none;
            }
            .dropdown-item.selected {
                background-color: var(--color-secondary);
                color: white;
            }
        </style>
    `;
    
    const input = container.querySelector(`#${fieldName}-input`);
    const dropdown = container.querySelector(`#${fieldName}-dropdown`);
    const selectedContainer = container.querySelector(`#${fieldName}-selected`);
    
    // Handle input focus and blur
    input.addEventListener('focus', () => {
        dropdown.style.display = 'block';
        filterDropdownItems('');
    });
    
    input.addEventListener('blur', (e) => {
        // Delay hiding to allow dropdown clicks
        setTimeout(() => {
            if (!container.contains(document.activeElement)) {
                dropdown.style.display = 'none';
            }
        }, 150);
    });
    
    // Handle input typing for filtering
    input.addEventListener('input', (e) => {
        filterDropdownItems(e.target.value);
    });
    
    // Handle dropdown item clicks
    dropdown.addEventListener('click', (e) => {
        const item = e.target.closest('.dropdown-item');
        if (item) {
            const value = item.dataset.value;
            if (!selectedItems.has(value)) {
                selectedItems.add(value);
                addSelectedItem(value, selectedContainer, fieldName);
                updateDropdownItemState(item, true);
            }
            input.value = '';
            input.focus();
        }
    });
    
    function filterDropdownItems(searchTerm) {
        const items = dropdown.querySelectorAll('.dropdown-item');
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            const matches = text.includes(searchTerm.toLowerCase());
            item.style.display = matches ? 'block' : 'none';
        });
    }
    
    function addSelectedItem(value, container, fieldName) {
        const itemElement = document.createElement('span');
        itemElement.className = 'selected-item';
        itemElement.innerHTML = `
            ${value}
            <span class="remove-btn" data-value="${value}">&times;</span>
            <input type="hidden" name="${fieldName}" value="${value}">
        `;
        
        itemElement.querySelector('.remove-btn').addEventListener('click', () => {
            selectedItems.delete(value);
            itemElement.remove();
            updateDropdownItemState(dropdown.querySelector(`[data-value="${value}"]`), false);
        });
        
        container.appendChild(itemElement);
    }
    
    function updateDropdownItemState(item, selected) {
        if (item) {
            item.classList.toggle('selected', selected);
            const icon = item.querySelector('i');
            if (icon) {
                icon.className = selected ? 'fas fa-check' : 'fas fa-plus';
            }
        }
    }
}

// Matching Interface Functionality
function initializeMatchingInterface() {
    const matchButton = document.getElementById('run-matching-btn');
    if (matchButton) {
        matchButton.addEventListener('click', function() {
            const studentId = this.dataset.studentId;
            if (studentId) {
                runMatching(studentId);
            }
        });
    }
    
    const matchAllButton = document.getElementById('match-all-btn');
    if (matchAllButton) {
        matchAllButton.addEventListener('click', runMatchingForAll);
    }
}

function runMatching(studentId) {
    const button = document.getElementById('run-matching-btn');
    const originalText = button.textContent;
    
    // Show loading state
    button.innerHTML = '<span class="spinner"></span> Finding Matches...';
    button.disabled = true;
    
    // Simulate processing time
    setTimeout(() => {
        window.location.href = `/match/${studentId}`;
    }, 2000);
}

function runMatchingForAll() {
    const button = document.getElementById('match-all-btn');
    const originalText = button.textContent;
    
    // Show loading state
    button.innerHTML = '<span class="spinner"></span> Matching All Students...';
    button.disabled = true;
    
    // Make API call
    fetch('/api/match-all')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Success', `Matched ${data.total_matches} students successfully!`, 'success');
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                showNotification('Error', 'Failed to run matching for all students.', 'error');
            }
        })
        .catch(error => {
            showNotification('Error', 'An error occurred while matching students.', 'error');
        })
        .finally(() => {
            button.textContent = originalText;
            button.disabled = false;
        });
}

// Progress Bar Animation
function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressBar = entry.target;
                const targetWidth = progressBar.dataset.progress || progressBar.style.width;
                
                progressBar.style.width = '0%';
                progressBar.style.transition = 'width 1.5s ease-in-out';
                
                setTimeout(() => {
                    progressBar.style.width = targetWidth;
                }, 100);
                
                observer.unobserve(progressBar);
            }
        });
    });
    
    progressBars.forEach(bar => observer.observe(bar));
}

// Tooltip Initialization
function initializeTooltips() {
    // Simple tooltip implementation
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = this.dataset.tooltip;
            tooltip.style.cssText = `
                position: absolute;
                background: var(--bg-card);
                color: var(--color-text);
                padding: 0.5rem 0.75rem;
                border-radius: 6px;
                font-size: 0.875rem;
                box-shadow: var(--shadow-lg);
                z-index: 1001;
                pointer-events: none;
                white-space: nowrap;
                border: 1px solid var(--border-color);
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
            
            this.tooltipElement = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this.tooltipElement) {
                this.tooltipElement.remove();
                this.tooltipElement = null;
            }
        });
    });
}

// Notification System
function showNotification(title, message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} notification`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1050;
        min-width: 300px;
        box-shadow: var(--shadow-lg);
    `;
    
    notification.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
            <div>
                <strong>${title}</strong><br>
                ${message}
            </div>
            <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// CGPA validation
function validateCGPA(input) {
    const value = parseFloat(input.value);
    if (value < 0 || value > 10) {
        input.setCustomValidity('CGPA must be between 0 and 10');
    } else {
        input.setCustomValidity('');
    }
}

// Age validation
function validateAge(input) {
    const value = parseInt(input.value);
    if (value < 18 || value > 35) {
        input.setCustomValidity('Age must be between 18 and 35');
    } else {
        input.setCustomValidity('');
    }
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading states to forms
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn && validateForm(this.id)) {
            const originalText = submitBtn.textContent;
            submitBtn.innerHTML = '<span class="spinner"></span> Processing...';
            submitBtn.disabled = true;
        }
    });
});
