/**
 * Real-time Form Validation Utility
 *
 * Provides instant validation feedback for form fields using the validation API.
 */

class FormValidator {
  constructor() {
    this.cache = new Map(); // Cache validation results
    this.validators = new Map(); // Store active validators
    this.debounceDelay = 500; // ms
  }

  /**
   * Initialize validation for a form
   * @param {string} formSelector - CSS selector for the form
   * @param {Object} fieldConfig - Configuration for fields to validate
   */
  init(formSelector, fieldConfig) {
    const form = document.querySelector(formSelector);
    if (!form) return;

    Object.entries(fieldConfig).forEach(([fieldName, config]) => {
      const input = form.querySelector(`[name="${fieldName}"]`);
      if (!input) return;

      this.setupFieldValidation(input, config);
    });
  }

  /**
   * Setup validation for a single field
   * @param {HTMLElement} input - Input element
   * @param {Object} config - Validation configuration
   */
  setupFieldValidation(input, config) {
    const fieldName = input.name;

    // Create feedback elements
    this.createFeedbackElements(input);

    // Setup event listeners
    input.addEventListener('input', () => {
      this.debounceValidate(fieldName, input, config);
    });

    input.addEventListener('blur', () => {
      this.validateField(fieldName, input, config);
    });
  }

  /**
   * Create feedback elements for validation messages
   * @param {HTMLElement} input - Input element
   */
  createFeedbackElements(input) {
    const container = input.parentElement;

    // Remove existing feedback
    const existing = container.querySelector('.validation-feedback');
    if (existing) existing.remove();

    // Create feedback container
    const feedback = document.createElement('div');
    feedback.className = 'validation-feedback mt-1 text-sm font-medium hidden';
    feedback.innerHTML = `
      <div class="validation-message flex items-center gap-2">
        <span class="validation-icon"></span>
        <span class="validation-text"></span>
      </div>
    `;

    container.appendChild(feedback);
  }

  /**
   * Debounced field validation
   * @param {string} fieldName - Field name
   * @param {HTMLElement} input - Input element
   * @param {Object} config - Validation configuration
   */
  debounceValidate(fieldName, input, config) {
    // Clear existing timeout
    if (this.validators.has(fieldName)) {
      clearTimeout(this.validators.get(fieldName));
    }

    // Set new timeout
    const timeoutId = setTimeout(() => {
      this.validateField(fieldName, input, config);
    }, this.debounceDelay);

    this.validators.set(fieldName, timeoutId);
  }

  /**
   * Validate a field using the API
   * @param {string} fieldName - Field name
   * @param {HTMLElement} input - Input element
   * @param {Object} config - Validation configuration
   */
  async validateField(fieldName, input, config) {
    const value = input.value.trim();

    // Skip validation if empty and not required
    if (!value && !config.required) {
      this.clearValidation(input);
      return;
    }

    // Show loading state
    this.showLoading(input);

    try {
      const cacheKey = `${fieldName}:${value}`;

      // Check cache first
      if (this.cache.has(cacheKey)) {
        const result = this.cache.get(cacheKey);
        this.displayResult(input, result);
        return;
      }

      // Make API request
      const response = await fetch(`/api/v1/validate/${config.endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({
          [fieldName]: value,
          ...(config.exclude || {})
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();

      // Cache result
      this.cache.set(cacheKey, result);

      // Display result
      this.displayResult(input, result);

    } catch (error) {
      console.error('Validation error:', error);
      this.showError(input, 'Validation failed. Please try again.');
    }
  }

  /**
   * Display validation result
   * @param {HTMLElement} input - Input element
   * @param {Object} result - Validation result
   */
  displayResult(input, result) {
    const feedback = input.parentElement.querySelector('.validation-feedback');
    const icon = feedback.querySelector('.validation-icon');
    const text = feedback.querySelector('.validation-text');

    // Remove all validation classes
    input.classList.remove('border-green-500', 'border-red-500', 'border-yellow-500');
    feedback.classList.remove('text-green-600', 'text-red-600', 'text-yellow-600');

    if (result.valid && result.available !== false) {
      // Valid and available
      input.classList.add('border-green-500');
      feedback.classList.add('text-green-600');
      icon.innerHTML = '✓';
      text.textContent = result.message;
      feedback.classList.remove('hidden');
    } else if (result.valid && result.available === false) {
      // Valid format but not available
      input.classList.add('border-yellow-500');
      feedback.classList.add('text-yellow-600');
      icon.innerHTML = '⚠';
      text.textContent = result.message;
      feedback.classList.remove('hidden');
    } else {
      // Invalid
      input.classList.add('border-red-500');
      feedback.classList.add('text-red-600');
      icon.innerHTML = '✗';
      text.textContent = result.message;
      feedback.classList.remove('hidden');
    }
  }

  /**
   * Show loading state
   * @param {HTMLElement} input - Input element
   */
  showLoading(input) {
    const feedback = input.parentElement.querySelector('.validation-feedback');
    const icon = feedback.querySelector('.validation-icon');
    const text = feedback.querySelector('.validation-text');

    input.classList.remove('border-green-500', 'border-red-500', 'border-yellow-500');
    feedback.classList.remove('text-green-600', 'text-red-600', 'text-yellow-600');
    feedback.classList.add('text-slate-500');

    icon.innerHTML = '⏳';
    text.textContent = 'Checking...';
    feedback.classList.remove('hidden');
  }

  /**
   * Show error state
   * @param {HTMLElement} input - Input element
   * @param {string} message - Error message
   */
  showError(input, message) {
    const feedback = input.parentElement.querySelector('.validation-feedback');
    const icon = feedback.querySelector('.validation-icon');
    const text = feedback.querySelector('.validation-text');

    input.classList.remove('border-green-500', 'border-yellow-500');
    input.classList.add('border-red-500');
    feedback.classList.remove('text-green-600', 'text-yellow-600', 'text-slate-500');
    feedback.classList.add('text-red-600');

    icon.innerHTML = '✗';
    text.textContent = message;
    feedback.classList.remove('hidden');
  }

  /**
   * Clear validation state
   * @param {HTMLElement} input - Input element
   */
  clearValidation(input) {
    const feedback = input.parentElement.querySelector('.validation-feedback');

    input.classList.remove('border-green-500', 'border-red-500', 'border-yellow-500');
    feedback.classList.add('hidden');
  }

  /**
   * Get CSRF token from meta tag
   * @returns {string} CSRF token
   */
  getCSRFToken() {
    const token = document.querySelector('meta[name=csrf-token]');
    return token ? token.getAttribute('content') : '';
  }

  /**
   * Batch validate multiple fields
   * @param {Object} fields - Fields to validate {fieldName: value}
   * @param {Object} config - Global configuration
   */
  async batchValidate(fields, config = {}) {
    try {
      const response = await fetch('/api/v1/validate/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({
          fields,
          ...config
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Batch validation error:', error);
      throw error;
    }
  }
}

// Global instance
window.formValidator = new FormValidator();

// Auto-initialize for common forms
document.addEventListener('DOMContentLoaded', function() {
  // Student creation/edit forms
  formValidator.init('#student-form, #create-student-form', {
    email: { endpoint: 'email', required: false },
    student_id: { endpoint: 'student-id', required: true },
    contact_number: { endpoint: 'phone', required: false },
    age: { endpoint: 'age', required: false }
  });

  // Faculty forms
  formValidator.init('#faculty-form, #create-faculty-form', {
    email: { endpoint: 'email', required: true },
    employee_id: { endpoint: 'employee-id', required: true },
    contact_number: { endpoint: 'phone', required: false }
  });

  // Subject forms
  formValidator.init('#subject-form, #create-subject-form', {
    subject_code: { endpoint: 'subject-code', required: true },
    code: { endpoint: 'subject-code', required: true }
  });

  // Section forms
  formValidator.init('#section-form, #create-section-form', {
    display_name: { endpoint: 'section-name', required: true }
  });
});

// Export for manual usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FormValidator;
}