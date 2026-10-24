// Global State
let recipes = [];
let currentRecipe = null;
let activeComponentId = null;
let checkedSteps = {};
let currentUnitSystem = 'metric'; // 'metric' or 'imperial'

const DB_NAME = 'RecipeStudioDB';
const DB_VERSION = 1;
const STORE_NAME = 'recipes';

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id' });
      }
    };
    request.onsuccess = (e) => resolve(e.target.result);
    request.onerror = (e) => reject(e.target.error);
  });
}

async function saveRecipeToDB(recipe) {
  const db = await openDB();
  const tx = db.transaction(STORE_NAME, 'readwrite');
  tx.objectStore(STORE_NAME).put(recipe);
  return tx.complete;
}

// System Unit Toggle
function setUnitSystem(system) {
  currentUnitSystem = system;
  const metricBtn = document.getElementById('unit-metric');
  const imperialBtn = document.getElementById('unit-imperial');

  if (system === 'metric') {
    metricBtn.className = 'px-2.5 py-1 rounded text-xs font-semibold bg-sky-600 text-white transition-colors';
    imperialBtn.className = 'px-2.5 py-1 rounded text-xs font-semibold text-slate-400 hover:text-white transition-colors';
  } else {
    imperialBtn.className = 'px-2.5 py-1 rounded text-xs font-semibold bg-sky-600 text-white transition-colors';
    metricBtn.className = 'px-2.5 py-1 rounded text-xs font-semibold text-slate-400 hover:text-white transition-colors';
  }

  renderVisualView();
}

// Convert Ingredient Units Dynamically
function formatIngredientDisplay(qty, unit, name) {
  if (currentUnitSystem === 'metric' || !unit) {
    return `${qty} ${unit}`;
  }

  const ingName = (name || '').toLowerCase();

  if (unit.toLowerCase() === 'g') {
    if (ingName.includes('flour')) {
      const cups = (qty / 120).toFixed(2);
      return `${cups.replace(/\.00$/, '')} cup (${Math.round(qty * 0.035274)} oz)`;
    }
    if (ingName.includes('sugar')) {
      const cups = (qty / 200).toFixed(2);
      return `${cups.replace(/\.00$/, '')} cup (${Math.round(qty * 0.035274)} oz)`;
    }
    if (ingName.includes('butter')) {
      const tbsp = (qty / 14.2).toFixed(1);
      return `${tbsp.replace(/\.0$/, '')} tbsp (${Math.round(qty * 0.035274)} oz)`;
    }
    const oz = (qty * 0.035274).toFixed(1);
    return `${oz.replace(/\.0$/, '')} oz`;
  }

  if (unit.toLowerCase() === 'ml') {
    if (qty <= 5) return `${(qty / 5).toFixed(1).replace(/\.0$/, '')} tsp`;
    if (qty <= 15) return `${(qty / 15).toFixed(1).replace(/\.0$/, '')} tbsp`;
    if (qty >= 240) return `${(qty / 240).toFixed(2).replace(/\.00$/, '')} cup`;
    const flOz = (qty / 29.5735).toFixed(1);
    return `${flOz.replace(/\.0$/, '')} fl oz`;
  }

  return `${qty} ${unit}`;
}

// Format Temperatures Dynamically
function formatTemperatureDisplay(val, unit) {
  if (!val) return '--';
  if (currentUnitSystem === 'imperial') {
    if (unit === 'C') {
      const fahrenheit = Math.round((val * 9 / 5) + 32);
      return `${fahrenheit}°F`;
    }
  }
  return `${val}°${unit || 'C'}`;
}

async function initApp() {
  try {
    const res = await fetch('recipes/index.json');
    const indexData = await res.json();

    recipes = []; // Reset local array to prevent duplicates

    for (const item of indexData) {
      const recRes = await fetch(`recipes/${item.file}`);
      const recJson = await recRes.json();
      recipes.push(recJson);
      await saveRecipeToDB(recJson); // Overwrite/sync with IndexedDB
    }

    renderRecipeList();
    if (recipes.length > 0) loadRecipe(recipes[0].id);
  } catch (err) {
    console.error('Initialization Error:', err);
  }
}

// Mobile Sidebar Handlers
const sidebar = document.getElementById('sidebar');
const backdrop = document.getElementById('sidebar-backdrop');
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const closeSidebarBtn = document.getElementById('close-sidebar-btn');

function openMobileSidebar() {
  sidebar?.classList.remove('-translate-x-full');
  backdrop?.classList.remove('hidden');
}

function closeMobileSidebar() {
  sidebar?.classList.add('-translate-x-full');
  backdrop?.classList.add('hidden');
}

mobileMenuBtn?.addEventListener('click', openMobileSidebar);
closeSidebarBtn?.addEventListener('click', closeMobileSidebar);
backdrop?.addEventListener('click', closeMobileSidebar);

function renderRecipeList(filter = '') {
  const listEl = document.getElementById('recipe-list');
  if (!listEl) return;
  listEl.innerHTML = '';

  const filtered = recipes.filter(r =>
    r.metadata.title.toLowerCase().includes(filter.toLowerCase()) ||
    (r.metadata.category && r.metadata.category.toLowerCase().includes(filter.toLowerCase()))
  );

  filtered.forEach(r => {
    const isActive = currentRecipe && currentRecipe.id === r.id;
    const btn = document.createElement('button');
    btn.onclick = () => {
      loadRecipe(r.id);
      closeMobileSidebar();
    };
    btn.className = `w-full text-left p-3 rounded-lg text-xs transition-all flex items-start justify-between gap-2 touch-target ${
      isActive 
        ? 'bg-sky-500/10 border border-sky-500/30 text-sky-300 font-semibold' 
        : 'hover:bg-slate-900 border border-transparent text-slate-400 hover:text-slate-200'
    }`;

    btn.innerHTML = `
      <div class="space-y-1 min-w-0">
        <div class="font-medium truncate text-slate-200">${escapeHTML(r.metadata.title)}</div>
        <div class="flex items-center space-x-2 text-[10px] text-slate-500">
          <span>${escapeHTML(r.metadata.category || 'General')}</span>
          <span>•</span>
          <span>${r.components ? r.components.length : 0} Components</span>
        </div>
      </div>
      <i class="fa-solid fa-chevron-right text-[10px] text-slate-600 mt-1"></i>
    `;
    listEl.appendChild(btn);
  });
}

document.getElementById('recipe-search')?.addEventListener('input', (e) => {
  renderRecipeList(e.target.value);
});

function loadRecipe(recipeId) {
  currentRecipe = recipes.find(r => r.id === recipeId);
  if (!currentRecipe) return;

  checkedSteps = {};

  if (currentRecipe.components && currentRecipe.components.length > 0) {
    activeComponentId = currentRecipe.components[0].component_id;
  } else {
    activeComponentId = null;
  }

  document.getElementById('breadcrumb-title').textContent = currentRecipe.metadata.title;
  renderRecipeList();
  renderVisualView();
  renderRawView();
}

function renderVisualView() {
  if (!currentRecipe) return;

  const meta = currentRecipe.metadata || {};
  const yld = currentRecipe.yield || {};

  document.getElementById('badge-category').textContent = meta.category || 'Recipe';
  document.getElementById('badge-cuisine').textContent = meta.cuisine || 'International';
  document.getElementById('recipe-title').textContent = meta.title;
  document.getElementById('recipe-description').textContent = meta.description || '';

  document.getElementById('metric-prep').textContent = `${meta.prep_time_minutes || 0} mins`;
  document.getElementById('metric-cook').textContent = `${meta.cook_time_minutes || 0} mins`;
  document.getElementById('metric-total').textContent = `${meta.total_time_minutes || 0} mins`;
  document.getElementById('metric-yield').textContent = `${yld.quantity || 1} ${yld.unit || 'serving'}`;

  const compTabsEl = document.getElementById('component-tabs');
  compTabsEl.innerHTML = '';

  const comps = currentRecipe.components || [];
  document.getElementById('component-count').textContent = `${comps.length} Component${comps.length === 1 ? '' : 's'}`;

  comps.forEach(comp => {
    const isActive = comp.component_id === activeComponentId;
    const btn = document.createElement('button');
    btn.onclick = () => selectComponent(comp.component_id);
    btn.className = `px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition-all shrink-0 touch-target ${
      isActive 
        ? 'bg-sky-600 text-white shadow-lg shadow-sky-600/20 border border-sky-400/30' 
        : 'bg-slate-950 hover:bg-slate-800 text-slate-400 border border-slate-800'
    }`;

    btn.innerHTML = `
      <i class="fa-solid fa-cube text-[10px]"></i>
      <span>${escapeHTML(comp.name)}</span>
    `;
    compTabsEl.appendChild(btn);
  });

  renderActiveComponentDetail();
  renderConstructionBlock();
}

function selectComponent(compId) {
  activeComponentId = compId;
  renderVisualView();
}

function renderActiveComponentDetail() {
  const activeComp = (currentRecipe.components || []).find(c => c.component_id === activeComponentId);

  const ingredientsEl = document.getElementById('component-ingredients-list');
  const stepsEl = document.getElementById('component-steps-list');
  const ingCountEl = document.getElementById('comp-ingredient-count');

  ingredientsEl.innerHTML = '';
  stepsEl.innerHTML = '';

  if (!activeComp) {
    ingredientsEl.innerHTML = '<p class="text-xs text-slate-500 italic">No component selected.</p>';
    stepsEl.innerHTML = '<p class="text-xs text-slate-500 italic">No steps available.</p>';
    return;
  }

  const ings = activeComp.ingredients || [];
  ingCountEl.textContent = `${ings.length} item${ings.length === 1 ? '' : 's'}`;

  ings.forEach(ing => {
    const item = document.createElement('div');
    item.className = 'p-2.5 bg-slate-900 border border-slate-800/80 rounded-lg flex items-center justify-between text-xs';
    item.innerHTML = `
      <div class="space-y-0.5">
        <span class="font-medium text-slate-200">${escapeHTML(ing.name)}</span>
        ${ing.preparation ? `<span class="text-[10px] text-slate-500 block">(${escapeHTML(ing.preparation)})</span>` : ''}
      </div>
      <span class="font-mono font-semibold text-sky-400 bg-sky-500/10 px-2 py-1 rounded border border-sky-500/20 shrink-0">
        ${formatIngredientDisplay(ing.quantity, ing.unit, ing.name)}
      </span>
    `;
    ingredientsEl.appendChild(item);
  });

  const compSteps = (currentRecipe.steps || []).filter(s => s.component_id === activeComponentId);
  compSteps.sort((a, b) => a.step_number - b.step_number);

  if (compSteps.length === 0) {
    stepsEl.innerHTML = '<p class="text-xs text-slate-500 italic">No explicit steps mapped for this component.</p>';
    return;
  }

  compSteps.forEach(step => {
    const stepKey = `${activeComponentId}_${step.step_number}`;
    const isChecked = checkedSteps[stepKey] || false;

    const card = document.createElement('div');
    card.className = `p-4 rounded-xl border transition-all ${
      isChecked ? 'bg-slate-900/40 border-slate-800/60 opacity-60' : 'bg-slate-900 border-slate-800 hover:border-slate-700'
    }`;

    card.innerHTML = `
      <div class="flex items-start gap-3">
        <label class="relative flex items-center cursor-pointer mt-0.5 shrink-0 touch-target">
          <input type="checkbox" ${isChecked ? 'checked' : ''} onchange="toggleStepCheck('${stepKey}')" class="sr-only custom-checkbox">
          <div class="w-5 h-5 border-2 border-slate-600 rounded bg-slate-950 flex items-center justify-center transition-colors">
            <i class="fa-solid fa-check text-xs text-white opacity-0 transition-opacity"></i>
          </div>
        </label>
        <div class="space-y-2 flex-1 min-w-0">
          <div class="flex items-center justify-between gap-2">
            <span class="text-xs font-bold text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded border border-sky-500/20">
              Step ${step.step_number}
            </span>
            ${step.technique ? `<span class="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">${escapeHTML(step.technique)}</span>` : ''}
          </div>
          <p class="text-xs text-slate-200 leading-relaxed ${isChecked ? 'line-through text-slate-400' : ''}">
            ${escapeHTML(step.instruction)}
          </p>
          ${(step.equipment && step.equipment.length > 0) ? `
            <div class="flex flex-wrap items-center gap-1.5 pt-1">
              <span class="text-[10px] text-slate-500">Tools:</span>
              ${step.equipment.map(e => `<span class="text-[10px] bg-slate-950 text-slate-400 px-1.5 py-0.5 rounded border border-slate-800">${escapeHTML(e)}</span>`).join('')}
            </div>
          ` : ''}
        </div>
      </div>
    `;
    stepsEl.appendChild(card);
  });
}

function toggleStepCheck(key) {
  checkedSteps[key] = !checkedSteps[key];
  renderActiveComponentDetail();
}

function resetStepCheckboxes() {
  checkedSteps = {};
  renderActiveComponentDetail();
}

function renderConstructionBlock() {
  const constr = currentRecipe.construction || {};
  const baking = constr.baking || {};
  const temp = baking.temperature || {};

  document.getElementById('baking-spec-content').innerHTML = `
    <div class="flex flex-wrap gap-x-6 gap-y-1">
      <div><strong class="text-slate-200">Temperature:</strong> ${formatTemperatureDisplay(temp.value, temp.unit)}</div>
      <div><strong class="text-slate-200">Duration:</strong> ${baking.duration_minutes || '--'} minutes</div>
      <div><strong class="text-slate-200">Container:</strong> ${escapeHTML(baking.container || 'Standard pan')}</div>
    </div>
  `;

  const assemblyListEl = document.getElementById('assembly-steps-list');
  assemblyListEl.innerHTML = '';

  const assemblySteps = constr.assembly_steps || [];
  if (assemblySteps.length === 0) {
    assemblyListEl.innerHTML = '<p class="text-xs text-slate-500 italic">No specific assembly steps provided.</p>';
    return;
  }

  assemblySteps.forEach(st => {
    const row = document.createElement('div');
    row.className = 'p-3 bg-slate-900 border border-slate-800/80 rounded-lg text-xs flex items-start space-x-3';
    row.innerHTML = `
      <div class="w-5 h-5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">${st.order}</div>
      <p class="text-slate-200 leading-relaxed">${escapeHTML(st.instruction)}</p>
    `;
    assemblyListEl.appendChild(row);
  });
}

function renderRawView() {
  if (!currentRecipe) return;
  document.getElementById('raw-json-editor').value = JSON.stringify(currentRecipe, null, 2);
}

function switchTab(tab) {
  const visualView = document.getElementById('view-visual');
  const rawView = document.getElementById('view-raw');
  const tabVisualBtn = document.getElementById('tab-visual');
  const tabRawBtn = document.getElementById('tab-raw');

  if (tab === 'visual') {
    visualView.classList.remove('hidden');
    rawView.classList.add('hidden');
    tabVisualBtn.className = 'px-3 py-1.5 rounded-md text-xs font-medium bg-sky-600 text-white flex items-center space-x-1.5 transition-colors whitespace-nowrap touch-target';
    tabRawBtn.className = 'px-3 py-1.5 rounded-md text-xs font-medium text-slate-400 hover:text-white flex items-center space-x-1.5 transition-colors whitespace-nowrap touch-target';
    renderVisualView();
  } else {
    visualView.classList.add('hidden');
    rawView.classList.remove('hidden');
    tabRawBtn.className = 'px-3 py-1.5 rounded-md text-xs font-medium bg-sky-600 text-white flex items-center space-x-1.5 transition-colors whitespace-nowrap touch-target';
    tabVisualBtn.className = 'px-3 py-1.5 rounded-md text-xs font-medium text-slate-400 hover:text-white flex items-center space-x-1.5 transition-colors whitespace-nowrap touch-target';
    renderRawView();
  }
}

async function saveEditedJSON() {
  const editor = document.getElementById('raw-json-editor');
  const errorBanner = document.getElementById('json-error-banner');
  const errorMsg = document.getElementById('json-error-message');

  try {
    const parsed = JSON.parse(editor.value);
    if (!parsed.id) parsed.id = `recipe_${Date.now()}`;

    await saveRecipeToDB(parsed);
    const idx = recipes.findIndex(r => r.id === parsed.id);
    if (idx !== -1) recipes[idx] = parsed;
    else recipes.push(parsed);

    currentRecipe = parsed;
    errorBanner.classList.add('hidden');
    renderRecipeList();
    switchTab('visual');
  } catch (err) {
    errorMsg.textContent = `JSON Error: ${err.message}`;
    errorBanner.classList.remove('hidden');
  }
}

function editRecipeJSON() { switchTab('raw'); }

function copyRawJSON() {
  const editor = document.getElementById('raw-json-editor');
  navigator.clipboard.writeText(editor.value);
  alert('Recipe JSON copied to clipboard!');
}

function openImportModal() { document.getElementById('import-modal').classList.remove('hidden'); }
function closeImportModal() { document.getElementById('import-modal').classList.add('hidden'); }

async function processImportJSON() {
  const text = document.getElementById('import-json-text').value;
  try {
    const parsed = JSON.parse(text);
    if (!parsed.id) parsed.id = `recipe_${Date.now()}`;
    await saveRecipeToDB(parsed);
    recipes.push(parsed);
    renderRecipeList();
    loadRecipe(parsed.id);
    closeImportModal();
  } catch (err) {
    alert('Invalid JSON Payload: ' + err.message);
  }
}

function exportCurrentRecipe() {
  if (!currentRecipe) return;
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentRecipe, null, 2));
  const downloadAnchor = document.createElement('a');
  downloadAnchor.setAttribute("href", dataStr);
  downloadAnchor.setAttribute("download", `${currentRecipe.metadata.title.toLowerCase().replace(/\s+/g, '-')}.json`);
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
}

function createNewRecipe() {
  const newRec = {
    "id": `recipe_${Date.now()}`,
    "metadata": {
      "title": "New Recipe Title",
      "description": "Enter recipe description here.",
      "cuisine": "French",
      "category": "Main Course",
      "prep_time_minutes": 20,
      "cook_time_minutes": 30,
      "total_time_minutes": 50
    },
    "yield": { "quantity": 2, "unit": "servings" },
    "components": [
      {
        "component_id": "comp_main",
        "name": "Main Component",
        "ingredients": [
          { "ingredient_id": "ing_1", "name": "Ingredient 1", "quantity": 100, "unit": "g" }
        ]
      }
    ],
    "steps": [
      {
        "step_number": 1,
        "component_id": "comp_main",
        "instruction": "First step instruction for main component.",
        "technique": "sear"
      }
    ],
    "construction": {
      "baking": { "temperature": { "value": 180, "unit": "C" }, "duration_minutes": 30, "container": "Pan" },
      "assembly_steps": [
        { "order": 1, "instruction": "Assemble and serve warm." }
      ]
    }
  };

  recipes.push(newRec);
  saveRecipeToDB(newRec);
  renderRecipeList();
  loadRecipe(newRec.id);
  switchTab('raw');
}

function escapeHTML(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, tag => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[tag] || tag));
}

window.addEventListener('DOMContentLoaded', initApp);