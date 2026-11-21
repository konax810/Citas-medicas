(() => {
  'use strict';

  const fieldSelector = 'input:not([type="submit"]):not([type="button"]):not([type="reset"]), select, textarea';

  const validationMessage = (field) => {
    const { validity } = field;
    if (validity.valueMissing) return 'Completa este campo.';
    if (validity.typeMismatch && field.type === 'email') return 'Escribe un correo electrónico válido.';
    if (validity.typeMismatch) return 'Revisa el formato de este valor.';
    if (validity.badInput) return 'Revisa el formato de este valor.';
    if (validity.rangeUnderflow) return `El valor debe ser igual o superior a ${field.min}.`;
    if (validity.rangeOverflow) return `El valor debe ser igual o inferior a ${field.max}.`;
    if (validity.stepMismatch) return 'Introduce un valor permitido.';
    if (validity.tooLong) return `Usa un máximo de ${field.maxLength} caracteres.`;
    if (validity.patternMismatch) return 'Revisa el formato indicado para este campo.';
    return 'Revisa este campo.';
  };

  const feedbackFor = (field) => {
    const feedbackId = `${field.id || field.name || 'field'}-feedback`;
    let feedback = document.getElementById(feedbackId);
    if (!feedback) {
      feedback = document.createElement('div');
      feedback.id = feedbackId;
      feedback.className = 'invalid-feedback';
      field.insertAdjacentElement('afterend', feedback);
    }
    return feedback;
  };

  const showFieldError = (field) => {
    const feedback = feedbackFor(field);
    feedback.textContent = validationMessage(field);
    field.classList.add('is-invalid');
    field.setAttribute('aria-invalid', 'true');

    const descriptions = new Set((field.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean));
    descriptions.add(feedback.id);
    field.setAttribute('aria-describedby', Array.from(descriptions).join(' '));
  };

  const clearFieldError = (field) => {
    field.classList.remove('is-invalid');
    field.removeAttribute('aria-invalid');
    const feedbackId = `${field.id || field.name || 'field'}-feedback`;
    document.getElementById(feedbackId)?.remove();

    const descriptions = (field.getAttribute('aria-describedby') || '').split(/\s+/).filter((id) => id && id !== feedbackId);
    if (descriptions.length) field.setAttribute('aria-describedby', descriptions.join(' '));
    else field.removeAttribute('aria-describedby');
  };

  const setupCharacterCount = (field) => {
    if (!field.matches('textarea[maxlength]')) return;
    const counter = document.createElement('div');
    counter.className = 'form-help character-count';
    counter.id = `${field.id || field.name || 'field'}-character-count`;
    counter.textContent = `${field.value.length} / ${field.maxLength} caracteres`;
    field.insertAdjacentElement('afterend', counter);

    const descriptions = new Set((field.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean));
    descriptions.add(counter.id);
    field.setAttribute('aria-describedby', Array.from(descriptions).join(' '));
    field.addEventListener('input', () => {
      counter.textContent = `${field.value.length} / ${field.maxLength} caracteres`;
    });
  };

  document.querySelectorAll('form[method="post"]:not([data-confirm-form])').forEach((form) => {
    const fields = Array.from(form.querySelectorAll(fieldSelector)).filter((field) => !field.disabled);
    fields.forEach(setupCharacterCount);

    fields.forEach((field) => {
      field.addEventListener('input', () => {
        if (field.validity.valid) clearFieldError(field);
      });
      field.addEventListener('change', () => {
        if (field.validity.valid) clearFieldError(field);
      });
    });

    form.addEventListener('submit', (event) => {
      if (form.dataset.submitting === 'true') {
        event.preventDefault();
        return;
      }

      const invalidFields = fields.filter((field) => !field.checkValidity());
      if (invalidFields.length) {
        event.preventDefault();
        invalidFields.forEach(showFieldError);
        const firstInvalid = invalidFields[0];
        firstInvalid.focus();
        const behavior = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
        firstInvalid.scrollIntoView({ block: 'center', behavior });
        return;
      }

      form.dataset.submitting = 'true';
      const submitButton = form.querySelector('button[type="submit"], button:not([type])');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.setAttribute('aria-busy', 'true');
        const spinner = document.createElement('span');
        spinner.className = 'spinner-border spinner-border-sm me-2';
        spinner.setAttribute('aria-hidden', 'true');
        submitButton.replaceChildren(spinner, document.createTextNode('Guardando…'));
      }
    });
  });
})();
