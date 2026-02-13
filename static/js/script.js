// Add smooth animations and interactions
document.addEventListener('DOMContentLoaded', function() {
    // Add focus animation to inputs
    const inputs = document.querySelectorAll('input, textarea');

    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });

    // Form validation with friendly messages
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredInputs = this.querySelectorAll('[required]');
            let isValid = true;

            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = '#f44336';

                    setTimeout(() => {
                        input.style.borderColor = '';
                    }, 2000);
                }
            });

            if (!isValid) {
                e.preventDefault();

                // Show friendly error message
                const errorMsg = document.createElement('p');
                errorMsg.textContent = '💔 Please fill out all fields!';
                errorMsg.style.color = '#f44336';
                errorMsg.style.marginTop = '10px';
                errorMsg.style.fontWeight = 'bold';
                errorMsg.className = 'error-message';

                const existingError = form.querySelector('.error-message');
                if (existingError) {
                    existingError.remove();
                }

                form.appendChild(errorMsg);

                setTimeout(() => {
                    errorMsg.remove();
                }, 3000);
            }
        });
    });

    // Add hover effect to buttons
    const buttons = document.querySelectorAll('.btn');

    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });

        button.addEventListener('mouseleave', function() {
            if (!this.id || this.id !== 'yesBtn') {
                this.style.transform = 'scale(1)';
            }
        });
    });
});

// Add sparkle effect on button clicks
function createSparkle(x, y) {
    const sparkle = document.createElement('div');
    sparkle.innerHTML = '✨';
    sparkle.style.position = 'fixed';
    sparkle.style.left = x + 'px';
    sparkle.style.top = y + 'px';
    sparkle.style.fontSize = '2rem';
    sparkle.style.pointerEvents = 'none';
    sparkle.style.zIndex = '9999';
    sparkle.style.animation = 'sparkle 1s ease-out forwards';

    document.body.appendChild(sparkle);

    setTimeout(() => {
        sparkle.remove();
    }, 1000);
}


// Add sparkle animation CSS dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes sparkle {
        0% {
            opacity: 1;
            transform: scale(0) rotate(0deg);
        }
        100% {
            opacity: 0;
            transform: scale(2) rotate(180deg) translateY(-50px);
        }
    }
`;
document.head.appendChild(style);

// Add sparkles to primary buttons
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('btn-primary') || e.target.classList.contains('btn-yes')) {
        for (let i = 0; i < 5; i++) {
            setTimeout(() => {
                createSparkle(
                    e.clientX + (Math.random() - 0.5) * 100,
                    e.clientY + (Math.random() - 0.5) * 100
                );
            }, i * 100);
        }
    }
});