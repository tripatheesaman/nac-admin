// Main JavaScript for Excel Processor

$(document).ready(function() {
    // Navbar enhancements
    initializeNavbar();
    
    // Initialize tooltips
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Add button click handler for debugging
    $('#submit-btn').on('click', function(e) {
        console.log('Process button clicked');
    });


    // File upload drag and drop functionality (unchanged)
    const fileUpload = document.getElementById('file-upload');
    if (fileUpload) {
        const uploadArea = fileUpload.closest('.mb-3');
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });
        function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }
        ['dragenter', 'dragover'].forEach(eventName => { uploadArea.addEventListener(eventName, highlight, false); });
        ['dragleave', 'drop'].forEach(eventName => { uploadArea.addEventListener(eventName, unhighlight, false); });
        function highlight(e) { uploadArea.classList.add('file-upload-area', 'dragover'); }
        function unhighlight(e) { uploadArea.classList.remove('file-upload-area', 'dragover'); }
        uploadArea.addEventListener('drop', handleDrop, false);
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            fileUpload.files = files;
            $(fileUpload).trigger('change');
        }
    }

    // --- AJAX upload-processing-polling logic ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function pollProgress(progress_id) {
        function check() {
            $.get('/app/progress/' + progress_id + '/', function(data) {
                // Update progress bar/spinner here as needed
                if (data.status === 'completed' || data.status === 'failed') {
                    $('#submit-btn').prop('disabled', false).html('Upload');
                    if (data.status === 'completed') {
                        showAlert('Processing complete!', 'success');
                        setTimeout(function() { location.reload(); }, 1500);
                    } else {
                        showAlert('Processing failed: ' + data.message, 'danger');
                    }
                } else {
                    setTimeout(check, 2000);
                }
            });
        }
        check();
    }

    function handleUploadSuccess(progress_id) {
        console.log('Sending process request for progress_id:', progress_id);
        $.ajax({
            url: '/app/process/' + progress_id + '/',
            type: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            success: function(response) {
                console.log('Process response:', response);
                pollProgress(progress_id);
            },
            error: function(xhr) {
                console.log('Process request failed:', xhr);
                showAlert('Processing failed to start.', 'danger');
                $('#submit-btn').prop('disabled', false).html('Upload');
            }
        });
    }

    // Handle form submission
    $('#upload-form').on('submit', function(e) {
        console.log('Form submit event triggered');
        e.preventDefault();
        const fileInput = $('#file-upload')[0];
        const file = fileInput.files[0];
        if (!file) {
            showAlert('Please select a file to upload.', 'warning');
            return false;
        }
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            showAlert('File size must be under 10MB.', 'warning');
            return false;
        }
        const allowedExtensions = ['.xlsx', '.xls'];
        const fileName = file.name.toLowerCase();
        const isValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));
        if (!isValidExtension) {
            showAlert('Only Excel files (.xlsx, .xls) are allowed.', 'warning');
            return false;
        }
        // Show loading state
        $('#submit-btn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>Processing...');
        var formData = new FormData(this);
        console.log('Sending upload request to /app/');
        $.ajax({
            url: '/app/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                console.log('Upload response:', response);
                if (response.success && response.progress_id) {
                    handleUploadSuccess(response.progress_id);
                } else {
                    showAlert('Upload failed.', 'danger');
                    $('#submit-btn').prop('disabled', false).html('Upload');
                }
            },
            error: function(xhr) {
                console.log('Upload request failed:', xhr);
                showAlert('Upload failed.', 'danger');
                $('#submit-btn').prop('disabled', false).html('Upload');
            }
        });
    });

    // Delete confirmation
    window.deleteFile = function(fileId, fileName) {
        if (!confirm('Are you sure you want to delete "' + fileName + '"? This action cannot be undone.')) {
            return;
        }
        $.ajax({
            url: '/app/files/' + fileId + '/delete/',
            type: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            success: function() {
                showAlert('File deleted successfully.', 'success');
                // Redirect to files list after a short delay
                setTimeout(function() { window.location.href = '/app/files/'; }, 800);
            },
            error: function(xhr) {
                var msg = 'Delete failed';
                if (xhr && xhr.responseText) { msg += ': ' + xhr.responseText; }
                showAlert(msg, 'danger');
            }
        });
    };

    // AJAX file processing
    window.processFile = function(fileId) {
        if (confirm('Start processing this file?')) {
            $.ajax({
                url: '/app/process/' + fileId + '/',
                type: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                success: function(response) {
                    if (response.success) {
                        showAlert('Processing started successfully!', 'success');
                        setTimeout(function() {
                            location.reload();
                        }, 2000);
                    } else {
                        showAlert('Error: ' + response.message, 'danger');
                    }
                },
                error: function() {
                    showAlert('An error occurred while processing the file.', 'danger');
                }
            });
        }
    };

    // Remove duplicate form validation handler. Only the AJAX handler above should be active.

    // Dynamic template upload field
    $('input[name="output_type"]').on('change', function() {
        const templateSection = $('#template-upload-section');
        if ($(this).val() === 'template') {
            templateSection.slideDown();
        } else {
            templateSection.slideUp();
        }
    });

    // File preview
    $('#file-upload').on('change', function() {
        const file = this.files[0];
        if (file) {
            const fileName = file.name;
            const fileSize = (file.size / 1024 / 1024).toFixed(2); // Convert to MB
            
            $(this).next('.form-text').html(
                '<i class="fas fa-check text-success"></i> Selected: ' + 
                fileName + ' (' + fileSize + ' MB)'
            );
        }
    });

    // Responsive table enhancements
    $('.table-responsive').each(function() {
        const table = $(this).find('table');
        const headers = table.find('thead th');
        
        table.find('tbody tr').each(function() {
            const cells = $(this).find('td');
            cells.each(function(index) {
                if (headers.length > index) {
                    $(this).attr('data-label', headers.eq(index).text().trim());
                }
            });
        });
    });

    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        const target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 100
            }, 500);
        }
    });

    // Keyboard shortcuts
    $(document).keydown(function(e) {
        // Ctrl/Cmd + Enter to submit form
        if ((e.ctrlKey || e.metaKey) && e.keyCode === 13) {
            $('#upload-form').submit();
        }
        
        // Escape to close alerts
        if (e.keyCode === 27) {
            $('.alert').fadeOut('slow');
        }
    });

    // Add fade-in animation to cards
    $('.card').addClass('fade-in');

    // Initialize any additional plugins
    initializePlugins();
});

// Show alert function
function showAlert(message, type) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('.messages').append(alertHtml);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        $('.alert').last().fadeOut('slow');
    }, 5000);
}

// Initialize additional plugins
function initializePlugins() {
    // Add any additional plugin initializations here
}

// Navbar functionality
function initializeNavbar() {
    // Add active class to current page
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-item-custom');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Smooth navbar brand hover effect
    const navbarBrand = document.querySelector('.navbar-brand');
    if (navbarBrand) {
        navbarBrand.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        navbarBrand.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    }
    
    // Rely on Bootstrap's dropdown behavior (click to open/close).
    // Removed custom hover-open logic that caused sticky menus.
    
    // Mobile menu enhancements
    const navbarToggler = document.querySelector('.custom-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
            
            // Add animation to mobile menu items
            const navItems = navbarCollapse.querySelectorAll('.nav-item-custom');
            navItems.forEach((item, index) => {
                if (navbarCollapse.classList.contains('show')) {
                    item.style.animationDelay = `${index * 0.1}s`;
                    item.classList.add('slide-in');
                } else {
                    item.classList.remove('slide-in');
                }
            });
        });
    }
    
    // Add scroll effect to navbar
    let lastScrollTop = 0;
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.custom-navbar');
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down
            navbar.style.transform = 'translateY(-100%)';
        } else {
            // Scrolling up
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
    });
}

// Export functions for global access
window.showAlert = showAlert; 