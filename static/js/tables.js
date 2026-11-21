(() => {
  'use strict';

  const normalize = (value) => value
    .toLocaleLowerCase('es-CO')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim();

  document.querySelectorAll('[data-table-search]').forEach((input) => {
    const tableId = input.getAttribute('aria-controls');
    const table = tableId ? document.getElementById(tableId) : null;
    const rows = Array.from(table?.querySelectorAll('tbody [data-table-row]') || []);
    const count = document.querySelector('[data-table-count]');
    const clearButton = document.querySelector('[data-table-clear]');
    const noResults = document.querySelector('[data-table-no-results]');
    const total = rows.length;

    if (!table || !count || !clearButton || !noResults) return;
    input.closest('[data-table-search-controls]')?.removeAttribute('hidden');
    document.getElementById('search-scope')?.removeAttribute('hidden');

    const update = () => {
      const query = normalize(input.value);
      let visibleRows = 0;

      rows.forEach((row) => {
        const matches = !query || normalize(row.textContent || '').includes(query);
        row.hidden = !matches;
        if (matches) visibleRows += 1;
      });

      count.textContent = query
        ? `${visibleRows} de ${total} ${total === 1 ? 'registro' : 'registros'}`
        : `${total} ${total === 1 ? 'registro' : 'registros'}`;
      clearButton.hidden = !query;
      noResults.hidden = !query || visibleRows > 0;
    };

    input.addEventListener('input', update);
    clearButton.addEventListener('click', () => {
      input.value = '';
      update();
      input.focus();
    });
  });
})();
