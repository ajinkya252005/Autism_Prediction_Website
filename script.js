// ===== DOM Ready =====
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initUsernameCheck();
    initPasswordStrength();
    initPasswordMatch();
    initFormValidations();
    initQuestionNavigation();
  });
  
  // ===== Username Availability Check =====
  function initUsernameCheck() {
    const usernameInput = document.getElementById('username');
    const availabilityText = document.getElementById('username-availability');
    
    if (!usernameInput || !availabilityText) return;
    
    let timeout;
    
    usernameInput.addEventListener('input', function() {
      clearTimeout(timeout);
      const username = this.value.trim();
      
      if (username.length < 3) {
        availabilityText.textContent = '';
        return;
      }
      
      // Show loading state
      availabilityText.textContent = 'Checking...';
      availabilityText.style.color = 'var(--gray)';
      
      timeout = setTimeout(() => {
        // Simulate API call (replace with actual fetch)
        setTimeout(() => {
          // Mock response - in real app, call your backend
          const isAvailable = Math.random() > 0.3; // 70% chance available
          
          if (isAvailable) {
            availabilityText.textContent = '✓ Available';
            availabilityText.style.color = 'var(--success)';
          } else {
            availabilityText.textContent = '✗ Already taken';
            availabilityText.style.color = 'var(--danger)';
          }
        }, 500);
      }, 300);
    });
  }
  
  // ===== Password Strength Meter =====
  function initPasswordStrength() {
    const passwordInput = document.getElementById('password');
    const strengthBar = document.querySelector('.strength-bar');
    const strengthText = document.querySelector('.strength-text');
    
    if (!passwordInput || !strengthBar || !strengthText) return;
    
    passwordInput.addEventListener('input', function() {
      const password = this.value;
      const strength = calculatePasswordStrength(password);
      
      // Update visual indicators
      strengthBar.style.width = `${strength.percentage}%`;
      strengthBar.style.backgroundColor = strength.color;
      strengthText.textContent = strength.text;
      strengthText.style.color = strength.color;
    });
  }
  
  function calculatePasswordStrength(password) {
    let score = 0;
    
    // Length check
    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 1;
    
    // Complexity checks
    if (/[A-Z]/.test(password)) score += 1; // Uppercase
    if (/[a-z]/.test(password)) score += 1; // Lowercase
    if (/[0-9]/.test(password)) score += 1; // Numbers
    if (/[^A-Za-z0-9]/.test(password)) score += 1; // Special chars
    
    // Determine strength level
    if (password.length === 0) {
      return {
        percentage: 0,
        color: 'transparent',
        text: ''
      };
    } else if (score <= 2) {
      return {
        percentage: 33,
        color: 'var(--danger)',
        text: 'Weak'
      };
    } else if (score <= 4) {
      return {
        percentage: 66,
        color: 'var(--warning)',
        text: 'Moderate'
      };
    } else {
      return {
        percentage: 100,
        color: 'var(--success)',
        text: 'Strong'
      };
    }
  }
  
  // ===== Password Match Check =====
  function initPasswordMatch() {
    const passwordInput = document.getElementById('password');
    const confirmInput = document.getElementById('confirm_password');
    const matchText = document.getElementById('password-match');
    
    if (!passwordInput || !confirmInput || !matchText) return;
    
    function checkMatch() {
      if (passwordInput.value && confirmInput.value) {
        if (passwordInput.value === confirmInput.value) {
          matchText.textContent = '✓ Passwords match';
          matchText.style.color = 'var(--success)';
        } else {
          matchText.textContent = '✗ Passwords do not match';
          matchText.style.color = 'var(--danger)';
        }
      } else {
        matchText.textContent = '';
      }
    }
    
    passwordInput.addEventListener('input', checkMatch);
    confirmInput.addEventListener('input', checkMatch);
  }
  
  // ===== Form Validations =====
  function initFormValidations() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
      form.addEventListener('submit', function(e) {
        const requiredFields = this.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
          if (!field.value.trim()) {
            field.style.borderColor = 'var(--danger)';
            isValid = false;
          } else {
            field.style.borderColor = '';
          }
        });
        
        if (!isValid) {
          e.preventDefault();
          alert('Please fill all required fields');
        }
      });
    });
  }
  
  // ===== Question Navigation =====
  function initQuestionNavigation() {
    // Save answers when navigating
    const answerForms = document.querySelectorAll('.answer-options form');
    
    answerForms.forEach(form => {
      form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Simulate saving answer
        const formData = new FormData(this);
        console.log('Answer saved:', Object.fromEntries(formData));
        
        // In real app, submit via fetch or proceed to next question
        const nextUrl = this.querySelector('button[type="submit"]').textContent.includes('Submit') 
          ? '/results' 
          : '/question/' + (parseInt(this.dataset.currentQuestion) + 1);
        
        window.location.href = nextUrl;
      });
    });
    
    // Animation for question transitions
    const questionCards = document.querySelectorAll('.question-card');
    if (questionCards.length) {
      questionCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.4s ease';
        
        setTimeout(() => {
          card.style.opacity = '1';
          card.style.transform = 'translateY(0)';
        }, 100);
      });
    }
  }
  
  // ===== Results Page Animations =====
  if (document.querySelector('.result-summary')) {
    const scoreCircle = document.querySelector('.score-circle');
    const resultDetails = document.querySelector('.result-details');
    
    // Animate score circle
    setTimeout(() => {
      scoreCircle.style.transform = 'scale(1.1)';
      setTimeout(() => {
        scoreCircle.style.transform = 'scale(1)';
      }, 300);
    }, 500);
    
    // Animate result details
    setTimeout(() => {
      resultDetails.style.opacity = '1';
      resultDetails.style.transform = 'translateY(0)';
    }, 800);
    
    // Initial state
    resultDetails.style.opacity = '0';
    resultDetails.style.transform = 'translateY(20px)';
    resultDetails.style.transition = 'all 0.6s ease';
  }