(() => {
  'use strict';

  const modalElement = document.getElementById('deleteConfirmationModal');
  const confirmButton = document.getElementById('confirmDeleteButton');
  const messageElement = document.getElementById('deleteConfirmationMessage');
  let pendingForm = null;

  if (!modalElement || !confirmButton || !messageElement) return;

  document.querySelectorAll('form[data-confirm-form]').forEach((form) => {
    form.dataset.confirmEnhanced = 'true';
  });

  const submitConfirmedForm = (form) => {
    if (form instanceof HTMLFormElement) {
      HTMLFormElement.prototype.submit.call(form);
    }
  };

  document.addEventListener('submit', (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement) || !form.hasAttribute('data-confirm-form')) return;

    event.preventDefault();
    const message = form.dataset.confirmMessage || '¿Deseas eliminar este registro?';
    messageElement.textContent = message;

    if (!window.bootstrap?.Modal) {
      if (window.confirm(message)) submitConfirmedForm(form);
      return;
    }

    pendingForm = form;
    window.bootstrap.Modal.getOrCreateInstance(modalElement).show();
  });

  confirmButton.addEventListener('click', () => {
    if (!pendingForm) return;
    const form = pendingForm;
    pendingForm = null;
    window.bootstrap.Modal.getOrCreateInstance(modalElement).hide();
    submitConfirmedForm(form);
  });

  modalElement.addEventListener('hidden.bs.modal', () => {
    pendingForm = null;
  });
})();
