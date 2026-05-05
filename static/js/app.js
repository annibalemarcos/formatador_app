const inputText = document.querySelector('#inputText');
const outputText = document.querySelector('#outputText');
const mode = document.querySelector('#mode');
const stats = document.querySelector('#stats');
const preview = document.querySelector('#preview');
const toastEl = document.querySelector('#toast');
const toastBody = document.querySelector('#toastBody');
const toast = new bootstrap.Toast(toastEl, { delay: 1800 });

const addBeforeText = document.querySelector('#addBeforeText');
const addAfterText = document.querySelector('#addAfterText');
const addBetweenText = document.querySelector('#addBetweenText');
const replaceFromText = document.querySelector('#replaceFromText');
const replaceToText = document.querySelector('#replaceToText');
const repeatCountText = document.querySelector('#repeatCountText');
const blankLinesBeforeCheck = document.querySelector('#blankLinesBeforeCheck');
const blankLinesAfterCheck = document.querySelector('#blankLinesAfterCheck');
const blankLinesBeforeCount = document.querySelector('#blankLinesBeforeCount');
const blankLinesAfterCount = document.querySelector('#blankLinesAfterCount');
const preserveSpacesCheck = document.querySelector('#preserveSpacesCheck');
const specialActionMode = document.querySelector('#specialActionMode');
const formatSpecialActionBtn = document.querySelector('#formatSpecialActionBtn');
const favoriteBtn = document.querySelector('#favoriteBtn');
const removeFavoriteBtn = document.querySelector('#removeFavoriteBtn');
const favoriteActionsDropdown = document.querySelector('#favoriteActionsDropdown');
const useFavoriteActionBtn = document.querySelector('#useFavoriteActionBtn');
const formatFavoriteActionBtn = document.querySelector('#formatFavoriteActionBtn');

const multiActionSelect = document.querySelector('#multiActionSelect');
const addMultiActionBtn = document.querySelector('#addMultiActionBtn');
const multiActionsList = document.querySelector('#multiActionsList');
const multiFavoriteName = document.querySelector('#multiFavoriteName');
const saveMultiFavoriteBtn = document.querySelector('#saveMultiFavoriteBtn');
const favoriteMultiDropdown = document.querySelector('#favoriteMultiDropdown');
const useFavoriteMultiBtn = document.querySelector('#useFavoriteMultiBtn');
const formatFavoriteMultiBtn = document.querySelector('#formatFavoriteMultiBtn');

const FAVORITES_KEY = 'formatador_action_favorites_v1';
const MULTI_FAVORITES_KEY = 'formatador_multi_action_favorites_v1';

let multiActions = [];

function notify(message) {
  toastBody.textContent = message;
  toast.show();
}

function getActionLabel(value) {
  const option = [...mode.options].find(opt => opt.value === value);
  return option ? option.textContent.trim() : value;
}

function getFavoriteActions() {
  return JSON.parse(localStorage.getItem(FAVORITES_KEY) || '[]');
}

function setFavoriteActions(values) {
  localStorage.setItem(FAVORITES_KEY, JSON.stringify(values));
}

function getFavoriteMultiActions() {
  return JSON.parse(localStorage.getItem(MULTI_FAVORITES_KEY) || '[]');
}

function setFavoriteMultiActions(values) {
  localStorage.setItem(MULTI_FAVORITES_KEY, JSON.stringify(values));
}

function refreshFavoriteDropdowns() {
  const favorites = getFavoriteActions();

  favoriteActionsDropdown.innerHTML = '';
  if (!favorites.length) {
    favoriteActionsDropdown.innerHTML = '<option value="">Nenhuma favorita ainda</option>';
  } else {
    favorites.forEach(value => {
      const option = document.createElement('option');
      option.value = value;
      option.textContent = getActionLabel(value);
      favoriteActionsDropdown.appendChild(option);
    });
  }

  const multiFavorites = getFavoriteMultiActions();
  favoriteMultiDropdown.innerHTML = '';
  if (!multiFavorites.length) {
    favoriteMultiDropdown.innerHTML = '<option value="">Nenhuma sequência favorita ainda</option>';
  } else {
    multiFavorites.forEach((item, index) => {
      const option = document.createElement('option');
      option.value = String(index);
      option.textContent = `${item.name} (${item.actions.map(getActionLabel).join(' → ')})`;
      favoriteMultiDropdown.appendChild(option);
    });
  }
}

function fillMultiActionSelect() {
  multiActionSelect.innerHTML = '';
  [...mode.options].forEach(option => {
    if (!option.value) return;
    const clone = document.createElement('option');
    clone.value = option.value;
    clone.textContent = option.textContent.trim();
    multiActionSelect.appendChild(clone);
  });
}

function renderMultiActions() {
  if (!multiActions.length) {
    multiActionsList.innerHTML = '<span class="text-secondary">Nenhuma ação adicionada ainda.</span>';
    return;
  }

  multiActionsList.innerHTML = '';
  multiActions.forEach((action, index) => {
    const row = document.createElement('div');
    row.className = 'multi-action-row d-flex align-items-center justify-content-between gap-2 border rounded-3 px-2 py-2 mb-2 bg-light';
    row.innerHTML = `
      <span><strong>${index + 1}.</strong> ${getActionLabel(action)}</span>
      <button class="btn btn-sm btn-outline-danger rounded-3" type="button" title="Remover da sequência">
        <i class="bi bi-x-lg"></i>
      </button>
    `;
    row.querySelector('button').addEventListener('click', () => {
      multiActions.splice(index, 1);
      renderMultiActions();
    });
    multiActionsList.appendChild(row);
  });
}

function updateStats() {
  const chars = outputText.value.length;
  const lines = outputText.value ? outputText.value.split(/\r?\n/).length : 0;
  stats.textContent = `${chars} caracteres • ${lines} linhas`;
}

async function formatText() {
  const payload = {
    text: inputText.value,
    mode: mode.value,
    add_before: addBeforeText ? addBeforeText.value : '',
    add_after: addAfterText ? addAfterText.value : '',
    add_between: addBetweenText ? addBetweenText.value : '',
    replace_from: replaceFromText ? replaceFromText.value : '',
    replace_to: replaceToText ? replaceToText.value : '',
    repeat_count: repeatCountText ? repeatCountText.value : 1,
    blank_lines_before: blankLinesBeforeCheck ? blankLinesBeforeCheck.checked : false,
    blank_lines_after: blankLinesAfterCheck ? blankLinesAfterCheck.checked : false,
    blank_lines_before_count: blankLinesBeforeCount ? blankLinesBeforeCount.value : 3,
    blank_lines_after_count: blankLinesAfterCount ? blankLinesAfterCount.value : 3,
    preserve_spaces: preserveSpacesCheck ? preserveSpacesCheck.checked : false
  };

  if (multiActions.length) {
    payload.actions = multiActions;
  }

  const response = await fetch('/api/format', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const data = await response.json();
  outputText.value = data.output || '';
  updateStats();
  renderPreview();
  notify(multiActions.length ? 'Múltiplas ações aplicadas. Combo bonito.' : 'Formatado. Agora o caos tem postura.');
}

function escapeHtml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function renderPreview() {
  const value = outputText.value;
  preview.innerHTML = value.trim()
    ? `<pre class="preview-plain mb-0">${escapeHtml(value)}</pre>`
    : '<span class="text-secondary">Nada para pré-visualizar ainda.</span>';
}

async function copyResult() {
  if (!outputText.value.trim()) {
    notify('Nada para copiar ainda.');
    return;
  }
  await navigator.clipboard.writeText(outputText.value);
  notify('Copiado para a área de transferência.');
}

async function exportResult() {
  if (!outputText.value.trim()) {
    notify('Gere algum resultado antes de exportar.');
    return;
  }
  const filename = document.querySelector('#filename').value || 'formatado.md';
  const response = await fetch('/api/export', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content: outputText.value, filename })
  });
  const data = await response.json();
  const box = document.querySelector('#exportBox');
  if (data.ok) {
    box.innerHTML = `<a class="link-success fw-semibold" href="${data.download_url}"><i class="bi bi-file-earmark-arrow-down me-1"></i>Baixar ${data.filename}</a>`;
    notify('Arquivo gerado. Lisinho.');
  }
}

function fillSample() {
  if (mode.value === 'python_list_vertical') {
    inputText.value = `py_list = ['Projeto A', 'Projeto B', 'Projeto A', 'Comprar café', 'Revisar código']`;
  } else if (mode.value === 'jsonificar_services') {
    inputText.value = `SERVICE_NAME:"Favoritos_app",
STATUS:"Activated",
ROOT_DIR:"C:\\xampp\\htdocs\\favoritos_app",
RUN_APP_PATH:"C:\\xampp\\htdocs\\favoritos_app\\app.py",
RUN_APP:"app.py",

SERVICE_NAME:"Bootstrap_lab",
STATUS:"Activated",
ROOT_DIR:"C:\\xampp\\htdocs\\bootstrap_lab",
RUN_APP_PATH:"C:\\xampp\\htdocs\\bootstrap_lab\\app.py",
RUN_APP:"app.py"`;
  } else if (mode.value === 'add_before') {
    inputText.value = `19981747092
19983718133
19993676929`;
    addBeforeText.value = '/fone';
  } else if (mode.value === 'add_after') {
    inputText.value = `19981747092
19983718133
19993676929`;
    addAfterText.value = '/fone';
  } else if (mode.value === 'add_between') {
    inputText.value = `Oi Mundo`;
    addBetweenText.value = '+';
  } else if (mode.value === 'replace_text') {
    inputText.value = `Oi Mundo cruel`;
    replaceFromText.value = 'cruel';
    replaceToText.value = 'feliz';
  } else if (mode.value === 'repeat_input') {
    inputText.value = `Oi Mundo feliz`;
    repeatCountText.value = '5';
  } else {
    inputText.value = `Projeto A\nProjeto B\nProjeto A\nComprar café\nRevisar código\nhttps://annibale.com.br\nhttps://annibale.com.br`;
  }
  notify('Exemplo carregado. Agora aperta o botão mágico.');
}

document.querySelector('#formatBtn').addEventListener('click', formatText);
document.querySelector('#copyBtn').addEventListener('click', copyResult);
document.querySelector('#clearBtn').addEventListener('click', () => {
  inputText.value = '';
  outputText.value = '';
  preview.innerHTML = '';
  multiActions = [];
  renderMultiActions();
  updateStats();
  notify('Tudo limpo. Tela zerada.');
});
document.querySelector('#sampleBtn').addEventListener('click', fillSample);
document.querySelector('#previewBtn').addEventListener('click', renderPreview);
document.querySelector('#exportBtn').addEventListener('click', exportResult);
outputText.addEventListener('input', () => { updateStats(); renderPreview(); });

favoriteBtn.addEventListener('click', () => {
  const favorites = getFavoriteActions();
  if (!favorites.includes(mode.value)) {
    favorites.push(mode.value);
    setFavoriteActions(favorites);
    refreshFavoriteDropdowns();
    notify(`Favoritado: ${getActionLabel(mode.value)}`);
  } else {
    notify('Essa ação já está nos favoritos.');
  }
});

removeFavoriteBtn.addEventListener('click', () => {
  const favorites = getFavoriteActions().filter(value => value !== mode.value);
  setFavoriteActions(favorites);
  refreshFavoriteDropdowns();
  notify(`Removido dos favoritos: ${getActionLabel(mode.value)}`);
});

useFavoriteActionBtn.addEventListener('click', () => {
  if (!favoriteActionsDropdown.value) {
    notify('Nenhuma ação favorita ainda.');
    return;
  }
  mode.value = favoriteActionsDropdown.value;
  notify(`Ação carregada: ${getActionLabel(mode.value)}`);
});

if (formatFavoriteActionBtn) {
  formatFavoriteActionBtn.addEventListener('click', () => {
    if (!favoriteActionsDropdown.value) {
      notify('Nenhuma ação favorita ainda.');
      return;
    }
    mode.value = favoriteActionsDropdown.value;
    multiActions = [];
    renderMultiActions();
    formatText();
  });
}

if (formatSpecialActionBtn) {
  formatSpecialActionBtn.addEventListener('click', () => {
    mode.value = specialActionMode ? specialActionMode.value : 'add_before';
    multiActions = [];
    renderMultiActions();
    formatText();
  });
}

addMultiActionBtn.addEventListener('click', () => {
  multiActions.push(multiActionSelect.value);
  renderMultiActions();
  notify(`Ação adicionada: ${getActionLabel(multiActionSelect.value)}`);
});

saveMultiFavoriteBtn.addEventListener('click', () => {
  if (!multiActions.length) {
    notify('Monte uma sequência antes de favoritar.');
    return;
  }

  const name = multiFavoriteName.value.trim() || `Sequência ${new Date().toLocaleString('pt-BR')}`;
  const favorites = getFavoriteMultiActions();

  favorites.push({ name, actions: [...multiActions] });
  setFavoriteMultiActions(favorites);
  refreshFavoriteDropdowns();
  multiFavoriteName.value = '';
  notify(`Sequência favorita salva: ${name}`);
});

useFavoriteMultiBtn.addEventListener('click', () => {
  const index = Number(favoriteMultiDropdown.value);
  const favorites = getFavoriteMultiActions();

  if (!favorites.length || Number.isNaN(index) || !favorites[index]) {
    notify('Nenhuma sequência favorita ainda.');
    return;
  }

  multiActions = [...favorites[index].actions];
  renderMultiActions();
  notify(`Sequência carregada: ${favorites[index].name}`);
});

if (formatFavoriteMultiBtn) {
  formatFavoriteMultiBtn.addEventListener('click', () => {
    const index = Number(favoriteMultiDropdown.value);
    const favorites = getFavoriteMultiActions();

    if (!favorites.length || Number.isNaN(index) || !favorites[index]) {
      notify('Nenhuma sequência favorita ainda.');
      return;
    }

    multiActions = [...favorites[index].actions];
    renderMultiActions();
    formatText();
  });
}

document.querySelectorAll('.preset').forEach(button => {
  button.addEventListener('click', () => {
    mode.value = button.dataset.mode;
    formatText();
  });
});

fillMultiActionSelect();
refreshFavoriteDropdowns();
renderMultiActions();
updateStats();
renderPreview();
