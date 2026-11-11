/**
 * OmniRisk Underwriting Cockpit - Frontend Application Logic
 * Integrates interactive form input, raw JSON editor, file upload, synthetic scenarios & relational Excel dataset
 */

let currentScenarios = [];
let activeScenarioId = null;
let latestReport = null;
let excelCustomers = [];
let currentExcelFilter = 'ALL';
let activeInputTab = 'tab-form';

// DOM Elements
const jsonEditor = document.getElementById('jsonEditor');
const scenarioGrid = document.getElementById('scenarioGrid');
const btnSynthesize = document.getElementById('btnSynthesize');
const btnFormatJson = document.getElementById('btnFormatJson');
const btnResetPayload = document.getElementById('btnResetPayload');
const btnSyncFromJson = document.getElementById('btnSyncFromJson');
const btnOpenBenchmark = document.getElementById('btnOpenBenchmark');
const btnCloseModal = document.getElementById('btnCloseModal');
const btnReRunBenchmark = document.getElementById('btnReRunBenchmark');
const benchmarkModal = document.getElementById('benchmarkModal');
const toast = document.getElementById('toast');
const inputModeBadge = document.getElementById('inputModeBadge');

// Ingestion Tab Elements
const inputTabsNav = document.getElementById('inputTabsNav');
const fileDropZone = document.getElementById('fileDropZone');
const fileInputJson = document.getElementById('fileInputJson');

// Form Input Elements
const formCustomerId = document.getElementById('formCustomerId');
const formEntityType = document.getElementById('formEntityType');
const formAge = document.getElementById('formAge');
const formCreditScore = document.getElementById('formCreditScore');
const formCreditTier = document.getElementById('formCreditTier');
const formGeoZone = document.getElementById('formGeoZone');
const formLineOfBusiness = document.getElementById('formLineOfBusiness');
const formRequestedLimit = document.getElementById('formRequestedLimit');
const formDeductible = document.getElementById('formDeductible');
const formAssetAge = document.getElementById('formAssetAge');
const formClaimsCount = document.getElementById('formClaimsCount');
const formPayoutAmount = document.getElementById('formPayoutAmount');
const formOpenClaims = document.getElementById('formOpenClaims');
const formEnvScore = document.getElementById('formEnvScore');
const formCoverageGap = document.getElementById('formCoverageGap');
const formPriorCancellation = document.getElementById('formPriorCancellation');

// Excel Dataset Elements
const excelSummaryTag = document.getElementById('excelSummaryTag');
const excelCustomerSelect = document.getElementById('excelCustomerSelect');
const btnLoadExcelCustomer = document.getElementById('btnLoadExcelCustomer');
const selCustId = document.getElementById('selCustId');
const selCustLoss = document.getElementById('selCustLoss');
const selCustStatus = document.getElementById('selCustStatus');

// Accounts Vault Elements
const btnOpenAccountsVault = document.getElementById('btnOpenAccountsVault');
const btnOpenVaultFromCard = document.getElementById('btnOpenVaultFromCard');
const accountsVaultModal = document.getElementById('accountsVaultModal');
const btnCloseVaultModal = document.getElementById('btnCloseVaultModal');
const vaultSearchInput = document.getElementById('vaultSearchInput');
const vaultTableBody = document.getElementById('vaultTableBody');
const vaultRecordCount = document.getElementById('vaultRecordCount');
let allVaultCustomers = [];
let activeVaultFilter = 'ALL';

// Customer Proof Elements
const btnInspectProofFromCard = document.getElementById('btnInspectProofFromCard');
const btnViewCustomerProof = document.getElementById('btnViewCustomerProof');
const customerProofModal = document.getElementById('customerProofModal');
const btnCloseProofModal = document.getElementById('btnCloseProofModal');
const proofSubtitle = document.getElementById('proofSubtitle');
const proofDemographicsBox = document.getElementById('proofDemographicsBox');
const proofPoliciesBody = document.getElementById('proofPoliciesBody');
const proofCoveragesBody = document.getElementById('proofCoveragesBody');
const proofClaimsBody = document.getElementById('proofClaimsBody');
const proofPaymentsBody = document.getElementById('proofPaymentsBody');
const proofPoliciesCount = document.getElementById('proofPoliciesCount');
const proofCoveragesCount = document.getElementById('proofCoveragesCount');
const proofClaimsCount = document.getElementById('proofClaimsCount');
const proofPaymentsCount = document.getElementById('proofPaymentsCount');
const btnSynthesizeFromProof = document.getElementById('btnSynthesizeFromProof');
let activeProofCustomerId = null;

// Portfolio Modal Elements
const btnOpenPortfolio = document.getElementById('btnOpenPortfolio');
const portfolioModal = document.getElementById('portfolioModal');
const btnClosePortfolioModal = document.getElementById('btnClosePortfolioModal');
const portApproveCount = document.getElementById('portApproveCount');
const portConditionalCount = document.getElementById('portConditionalCount');
const portDeclineCount = document.getElementById('portDeclineCount');
const portAvgSpeed = document.getElementById('portAvgSpeed');
const portfolioTableBody = document.getElementById('portfolioTableBody');

// Cockpit Status Elements
const activeEngineText = document.getElementById('activeEngineText');
const verdictBadge = document.getElementById('verdictBadge');
const verdictText = document.getElementById('verdictText');
const verdictExplanation = document.getElementById('verdictExplanation');
const riskTierText = document.getElementById('riskTierText');
const confidenceText = document.getElementById('confidenceText');
const latencyText = document.getElementById('latencyText');

const kriContainer = document.getElementById('kriContainer');
const kriCountBadge = document.getElementById('kriCountBadge');
const executiveSummaryText = document.getElementById('executiveSummaryText');
const conditionsList = document.getElementById('conditionsList');
const suggestedDeductibleText = document.getElementById('suggestedDeductibleText');

const valFreq = document.getElementById('valFreq');
const valSeverity = document.getElementById('valSeverity');
const valLossRatio = document.getElementById('valLossRatio');
const valHazardScore = document.getElementById('valHazardScore');
const valRiskScore = document.getElementById('valRiskScore');

const sliderDeductible = document.getElementById('sliderDeductible');
const sliderHazard = document.getElementById('sliderHazard');
const valDeductible = document.getElementById('valDeductible');
const valHazard = document.getElementById('valHazard');
const btnApplyWhatIf = document.getElementById('btnApplyWhatIf');

const btnCopySummary = document.getElementById('btnCopySummary');
const btnExportSlip = document.getElementById('btnExportSlip');

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
  initHealthCheck();
  setupInputTabs();
  setupFormEventListeners();
  setupFileUpload();
  loadScenarios();
  loadExcelDataset();
  setupEventListeners();
});

function showToast(msg) {
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3200);
}

// 1. Ingestion Tabs Switching
function setupInputTabs() {
  const tabBtns = document.querySelectorAll('.input-tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const targetId = btn.getAttribute('data-tab');
      activeInputTab = targetId;

      document.querySelectorAll('.tab-pane').forEach(p => p.classList.add('hidden'));
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.remove('hidden');

      if (targetId === 'tab-form') {
        inputModeBadge.textContent = 'Interactive Form Mode';
        syncFormFromJson();
      } else if (targetId === 'tab-json') {
        inputModeBadge.textContent = 'Raw JSON Mode';
        syncJsonFromForm();
      } else if (targetId === 'tab-upload') {
        inputModeBadge.textContent = 'File Upload Mode';
      }
    });
  });
}

// 2. Interactive Form Two-Way Synchronization
function getSelectedPerils() {
  const checkboxes = document.querySelectorAll('input[name="formPerils"]:checked');
  return Array.from(checkboxes).map(cb => cb.value);
}

function buildPayloadFromForm() {
  const custId = formCustomerId ? formCustomerId.value.trim() || 'SYNTH-USER-01' : 'SYNTH-USER-01';
  const entityType = formEntityType ? formEntityType.value : 'INDIVIDUAL';
  const age = formAge ? Number(formAge.value) || 44 : 44;
  const creditScore = formCreditScore ? Number(formCreditScore.value) || 730 : 730;
  const creditTier = formCreditTier ? formCreditTier.value : 'GOOD';
  const geoZone = formGeoZone ? formGeoZone.value : 'TIER_2_INLAND_MIDWEST';

  const lob = formLineOfBusiness ? formLineOfBusiness.value : 'PROPERTY_HOMEOWNERS';
  const reqLimit = formRequestedLimit ? Number(formRequestedLimit.value) || 500000 : 500000;
  const deductible = formDeductible ? Number(formDeductible.value) || 2500 : 2500;
  const assetAge = formAssetAge ? Number(formAssetAge.value) || 12 : 12;

  const claimCount = formClaimsCount ? Number(formClaimsCount.value) || 0 : 0;
  const payoutAmount = formPayoutAmount ? Number(formPayoutAmount.value) || 0 : 0;
  const openClaims = formOpenClaims ? Number(formOpenClaims.value) || 0 : 0;
  const perils = getSelectedPerils();

  const envScore = formEnvScore ? Number(formEnvScore.value) || 35 : 35;
  const coverageGap = formCoverageGap ? Number(formCoverageGap.value) || 0 : 0;
  const priorCancel = formPriorCancellation ? formPriorCancellation.checked : false;

  // Build incident records
  const incidents = [];
  const perilsList = perils.length > 0 ? perils : ['Property Damage'];
  for (let i = 0; i < claimCount; i++) {
    const perilName = perilsList[i % perilsList.length];
    const indPayout = claimCount > 0 ? Math.round(payoutAmount / claimCount) : 0;
    incidents.push({
      year: 2026 - (i + 1),
      peril: perilName,
      payout_usd: indPayout,
      at_fault: i % 2 === 1,
      description: `${perilName} loss incident reported by policyholder`
    });
  }

  const specialHazards = [];
  if (geoZone.includes('COASTAL')) specialHazards.push('COASTAL_HURRICANE_ZONE');
  if (geoZone.includes('WILDFIRE')) specialHazards.push('WILDFIRE_URBAN_INTERFACE');
  if (claimCount >= 3) specialHazards.push('HIGH_CLAIM_FREQUENCY');
  if (priorCancel) specialHazards.push('PRIOR_CARRIER_NON_RENEWAL');

  return {
    customer_id: custId,
    entity_type: entityType,
    demographics: {
      age: entityType === 'INDIVIDUAL' ? age : null,
      years_in_business: entityType === 'COMMERCIAL' ? age : null,
      credit_score: creditScore,
      credit_tier: creditTier,
      geographic_risk_zone: geoZone,
      annual_revenue_usd: entityType === 'COMMERCIAL' ? 1200000 : null
    },
    policy_request: {
      line_of_business: lob,
      requested_limit_usd: reqLimit,
      deductible_usd: deductible,
      asset_age_years: assetAge,
      asset_category_or_construction: lob.includes('AUTO') ? 'Commercial Fleet Class 4' : 'Masonry Non-Combustible',
      protection_class_or_security: 'Standard Monitored Protection'
    },
    claim_history: {
      years_of_history: 5,
      total_claims_count: claimCount,
      total_payout_amount_usd: payoutAmount,
      open_claims_count: openClaims,
      incidents: incidents
    },
    external_risk_factors: {
      prior_carrier_cancellation: priorCancel,
      gap_in_coverage_months: coverageGap,
      environmental_hazard_score: envScore,
      crime_hazard_score: geoZone.includes('METRO') ? 60.0 : 25.0,
      safety_compliance_certified: !priorCancel,
      special_hazards: specialHazards
    }
  };
}

function syncJsonFromForm() {
  const payload = buildPayloadFromForm();
  if (jsonEditor) {
    jsonEditor.value = JSON.stringify(payload, null, 2);
  }
  syncWhatIfSliders(payload);
}

function syncFormFromJson() {
  try {
    const payload = JSON.parse(jsonEditor.value);
    populateFormFromPayload(payload);
  } catch (e) {
    // Keep form as is if JSON is currently invalid
  }
}

function populateFormFromPayload(p) {
  if (!p) return;
  if (formCustomerId && p.customer_id) formCustomerId.value = p.customer_id;
  if (formEntityType && p.entity_type) formEntityType.value = p.entity_type;

  const d = p.demographics || {};
  if (formAge && (d.age || d.years_in_business)) formAge.value = d.age || d.years_in_business;
  if (formCreditScore && d.credit_score) formCreditScore.value = d.credit_score;
  if (formCreditTier && d.credit_tier) formCreditTier.value = d.credit_tier;
  if (formGeoZone && d.geographic_risk_zone) {
    // If not in select options, add temporary option
    let found = false;
    for (let opt of formGeoZone.options) {
      if (opt.value === d.geographic_risk_zone) { found = true; break; }
    }
    if (!found) {
      const opt = document.createElement('option');
      opt.value = d.geographic_risk_zone;
      opt.textContent = d.geographic_risk_zone;
      formGeoZone.appendChild(opt);
    }
    formGeoZone.value = d.geographic_risk_zone;
  }

  const pol = p.policy_request || {};
  if (formLineOfBusiness && pol.line_of_business) formLineOfBusiness.value = pol.line_of_business;
  if (formRequestedLimit && pol.requested_limit_usd) formRequestedLimit.value = pol.requested_limit_usd;
  if (formDeductible && pol.deductible_usd) formDeductible.value = pol.deductible_usd;
  if (formAssetAge && pol.asset_age_years !== undefined) formAssetAge.value = pol.asset_age_years;

  const ch = p.claim_history || {};
  if (formClaimsCount && ch.total_claims_count !== undefined) formClaimsCount.value = ch.total_claims_count;
  if (formPayoutAmount && ch.total_payout_amount_usd !== undefined) formPayoutAmount.value = ch.total_payout_amount_usd;
  if (formOpenClaims && ch.open_claims_count !== undefined) formOpenClaims.value = ch.open_claims_count;

  // Set peril checkboxes based on incidents
  const incidentPerils = new Set((ch.incidents || []).map(i => i.peril));
  document.querySelectorAll('input[name="formPerils"]').forEach(cb => {
    cb.checked = incidentPerils.has(cb.value);
  });

  const ext = p.external_risk_factors || {};
  if (formEnvScore && ext.environmental_hazard_score !== undefined) formEnvScore.value = ext.environmental_hazard_score;
  if (formCoverageGap && ext.gap_in_coverage_months !== undefined) formCoverageGap.value = ext.gap_in_coverage_months;
  if (formPriorCancellation && ext.prior_carrier_cancellation !== undefined) formPriorCancellation.checked = ext.prior_carrier_cancellation;
}

function setupFormEventListeners() {
  const formInputs = [
    formCustomerId, formEntityType, formAge, formCreditScore, formCreditTier,
    formGeoZone, formLineOfBusiness, formRequestedLimit, formDeductible, formAssetAge,
    formClaimsCount, formPayoutAmount, formOpenClaims, formEnvScore, formCoverageGap,
    formPriorCancellation
  ];

  formInputs.forEach(input => {
    if (input) {
      input.addEventListener('input', syncJsonFromForm);
      input.addEventListener('change', syncJsonFromForm);
    }
  });

  // Credit Score auto-tiering
  if (formCreditScore && formCreditTier) {
    formCreditScore.addEventListener('input', () => {
      const score = Number(formCreditScore.value);
      if (score >= 750) formCreditTier.value = 'EXCELLENT';
      else if (score >= 670) formCreditTier.value = 'GOOD';
      else if (score >= 580) formCreditTier.value = 'FAIR';
      else formCreditTier.value = 'POOR';
      syncJsonFromForm();
    });
  }

  document.querySelectorAll('input[name="formPerils"]').forEach(cb => {
    cb.addEventListener('change', syncJsonFromForm);
  });

  if (btnSyncFromJson) {
    btnSyncFromJson.addEventListener('click', () => {
      syncFormFromJson();
      showToast('Form fields synchronized from JSON payload.');
    });
  }
}

// 3. File Upload Handler
function setupFileUpload() {
  if (!fileDropZone || !fileInputJson) return;

  fileDropZone.addEventListener('click', () => fileInputJson.click());

  fileInputJson.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) handleUploadedFile(file);
  });

  fileDropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileDropZone.classList.add('dragover');
  });

  fileDropZone.addEventListener('dragleave', () => fileDropZone.classList.remove('dragover'));

  fileDropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    fileDropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleUploadedFile(e.dataTransfer.files[0]);
    }
  });
}

function handleUploadedFile(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const payload = JSON.parse(e.target.result);
      jsonEditor.value = JSON.stringify(payload, null, 2);
      populateFormFromPayload(payload);
      syncWhatIfSliders(payload);
      showToast(`Loaded payload from ${file.name}`);
      synthesizeRiskProfile();
    } catch (err) {
      showToast('Invalid JSON file. Please ensure it follows the OmniRisk schema.');
    }
  };
  reader.readAsText(file);
}

// 4. Health Check & Engine Discovery
async function initHealthCheck() {
  try {
    const res = await fetch('/api/health');
    if (res.ok) {
      const data = await res.json();
      activeEngineText.textContent = data.active_engine;
      if (data.excel_dataset_loaded && excelSummaryTag) {
        excelSummaryTag.textContent = `${data.excel_total_customers} Accounts Available`;
      }
    }
  } catch (err) {
    activeEngineText.textContent = 'OmniRisk Local Engine';
  }
}

// 5. Load Synthetic Scenarios
async function loadScenarios() {
  try {
    const res = await fetch('/api/scenarios');
    if (res.ok) {
      currentScenarios = await res.json();
      renderScenarioButtons(currentScenarios);
      if (currentScenarios.length > 0) {
        selectScenario(currentScenarios[0].id);
      }
    }
  } catch (err) {
    console.error('Failed to load scenarios:', err);
  }
}

function renderScenarioButtons(scenarios) {
  scenarioGrid.innerHTML = '';
  scenarios.forEach((s) => {
    const btn = document.createElement('div');
    btn.className = `scenario-btn ${activeScenarioId === s.id ? 'active' : ''}`;
    btn.id = `btn-scenario-${s.id}`;
    btn.innerHTML = `
      <span class="scenario-badge badge-${s.badge_color}">${s.badge}</span>
      <div class="scenario-name">${s.name.split(':')[0]}</div>
      <div class="scenario-sub">${s.description}</div>
    `;
    btn.addEventListener('click', () => selectScenario(s.id));
    scenarioGrid.appendChild(btn);
  });
}

async function selectScenario(id) {
  activeScenarioId = id;
  document.querySelectorAll('.scenario-btn').forEach(b => b.classList.remove('active'));
  const activeBtn = document.getElementById(`btn-scenario-${id}`);
  if (activeBtn) activeBtn.classList.add('active');

  try {
    const res = await fetch(`/api/scenarios/${id}`);
    if (res.ok) {
      const payload = await res.json();
      jsonEditor.value = JSON.stringify(payload, null, 2);
      populateFormFromPayload(payload);
      syncWhatIfSliders(payload);
      synthesizeRiskProfile();
    }
  } catch (err) {
    showToast('Failed to load scenario payload.');
  }
}

// 6. Excel Dataset Explorer Functions
async function loadExcelDataset() {
  try {
    const summaryRes = await fetch('/api/dataset/summary');
    if (summaryRes.ok) {
      const s = await summaryRes.json();
      if (excelSummaryTag) {
        excelSummaryTag.textContent = `${s.total_customers} Accounts | $${(s.total_loss_incurred_usd / 1000000).toFixed(1)}M Losses`;
      }
    }
    await filterExcelCustomers('ALL');
  } catch (err) {
    console.warn('Excel dataset service error:', err);
  }
}

async function filterExcelCustomers(filterType) {
  currentExcelFilter = filterType;
  try {
    const res = await fetch(`/api/dataset/customers?filter_type=${filterType}&limit=120`);
    if (res.ok) {
      excelCustomers = await res.json();
      renderCustomerSelect(excelCustomers);
    }
  } catch (err) {
    showToast('Failed to load Excel customers.');
  }
}

function renderCustomerSelect(customers) {
  if (!excelCustomerSelect) return;
  excelCustomerSelect.innerHTML = '';

  if (customers.length === 0) {
    excelCustomerSelect.innerHTML = '<option value="">No matching accounts found</option>';
    updateSelectedStrip(null);
    return;
  }

  customers.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.customer_id;
    const lossStr = c.total_claims_amount > 0 ? `$${(c.total_claims_amount / 1000).toFixed(0)}k` : '$0';
    const lapseStr = c.has_lapsed ? ' [Lapsed]' : '';
    opt.textContent = `${c.customer_id} | ${c.city}, ${c.state} | ${c.claim_count} Claim(s) (${lossStr})${lapseStr}`;
    excelCustomerSelect.appendChild(opt);
  });

  updateSelectedStrip(customers[0]);
}

function updateSelectedStrip(cust) {
  if (!cust) {
    if (selCustId) selCustId.textContent = '--';
    if (selCustLoss) selCustLoss.textContent = '$0';
    if (selCustStatus) selCustStatus.textContent = '--';
    return;
  }
  if (selCustId) selCustId.textContent = cust.customer_id;
  if (selCustLoss) selCustLoss.textContent = `$${Number(cust.total_claims_amount).toLocaleString()}`;
  if (selCustStatus) {
    selCustStatus.textContent = cust.tag_badge;
    selCustStatus.style.color = cust.badge_color === 'rose' ? '#fb7185' : (cust.badge_color === 'amber' ? '#fbbf24' : '#34d399');
  }
}

async function loadAndSynthesizeCustomerId(custId) {
  if (!custId) return;
  try {
    const res = await fetch(`/api/dataset/customer/${custId}`);
    if (!res.ok) throw new Error('Customer transformation failed');
    const payload = await res.json();

    document.querySelectorAll('.scenario-btn').forEach(b => b.classList.remove('active'));
    activeScenarioId = null;

    if (excelCustomerSelect) excelCustomerSelect.value = custId;
    const matchedCust = excelCustomers.find(c => c.customer_id === custId) || allVaultCustomers.find(c => c.customer_id === custId);
    if (matchedCust) updateSelectedStrip(matchedCust);

    jsonEditor.value = JSON.stringify(payload, null, 2);
    populateFormFromPayload(payload);
    syncWhatIfSliders(payload);
    activeProofCustomerId = custId;
    synthesizeRiskProfile();
    showToast(`Loaded ${custId} from insurance_model.xlsx`);
  } catch (err) {
    showToast(`Error: ${err.message}`);
  }
}

async function loadAndSynthesizeExcelCustomer() {
  const custId = excelCustomerSelect ? excelCustomerSelect.value : null;
  if (!custId) {
    showToast('Please select an account from the Excel dropdown.');
    return;
  }
  await loadAndSynthesizeCustomerId(custId);
}

// Relational Proof Modal Viewer
async function openCustomerProof(custId) {
  if (!custId) {
    showToast('Please select a customer first.');
    return;
  }
  activeProofCustomerId = custId;
  customerProofModal.classList.add('active');
  proofSubtitle.textContent = `Source records for ${custId} directly extracted from insurance_model.xlsx (Zero-PII compliant).`;
  proofDemographicsBox.innerHTML = '<div style="color: var(--text-muted); padding: 0.5rem 0;">Loading verifiable proof records from Excel...</div>';
  proofPoliciesBody.innerHTML = '';
  proofCoveragesBody.innerHTML = '';
  proofClaimsBody.innerHTML = '';
  proofPaymentsBody.innerHTML = '';

  try {
    const res = await fetch(`/api/dataset/customer/${custId}/proof`);
    if (!res.ok) throw new Error('Failed to retrieve proof records');
    const data = await res.json();

    const d = data.demographics_proof || {};
    const w = data.wide_summary || {};
    proofDemographicsBox.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.6rem;">
        <div>Customer ID: <strong style="color: #60a5fa;">${d.customer_id}</strong></div>
        <div>Date of Birth: <strong>${d.dob}</strong> (Calculated Age: <strong>${d.calculated_age}</strong>)</div>
        <div>Location / Jurisdiction: <strong>${d.city}, ${d.state}</strong> (${w.region || 'Central'} Region)</div>
        <div>Assigned Underwriter/Agent: <strong>${w.agent_name || 'Agent'}</strong></div>
        <div>Total Premium Paid: <strong style="color: #34d399;">$${Number(w.total_paid_to_date || 0).toLocaleString()}</strong></div>
        <div>Total Historical Losses: <strong style="color: #fb7185;">$${Number(w.total_claims_amount || 0).toLocaleString()}</strong></div>
      </div>
      <div style="margin-top: 0.5rem; color: #a7f3d0; font-size: 0.72rem; display: flex; align-items: center; gap: 0.4rem;">
        <span>🛡️</span> <span>${d.pii_compliance} | Provenance File: <code>${data.audit_trail?.source_file || 'insurance_model.xlsx'}</code></span>
      </div>
    `;

    proofPoliciesCount.textContent = `${data.policies?.length || 0} Records`;
    proofPoliciesBody.innerHTML = (data.policies || []).map(p => `
      <tr>
        <td><strong style="color: #38bdf8;">${p.policy_id}</strong></td>
        <td>${p.product_name} (${p.product_id})</td>
        <td><span class="proof-badge" style="background: ${p.status.toLowerCase() === 'lapsed' ? 'rgba(244,63,94,0.2)' : 'rgba(16,185,129,0.2)'}; color: ${p.status.toLowerCase() === 'lapsed' ? '#fb7185' : '#34d399'};">${p.status}</span></td>
        <td>$${Number(p.sum_insured_usd).toLocaleString()}</td>
        <td>$${Number(p.annual_premium_usd).toLocaleString()}</td>
        <td>${p.term_months} mos</td>
        <td>${p.start_date}</td>
        <td>${p.end_date}</td>
      </tr>
    `).join('') || '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 0.6rem;">No policies found</td></tr>';

    proofCoveragesCount.textContent = `${data.coverages?.length || 0} Records`;
    proofCoveragesBody.innerHTML = (data.coverages || []).map(c => `
      <tr>
        <td><strong>${c.policy_id}</strong></td>
        <td><code>${c.coverage_id}</code></td>
        <td><strong style="color: #c084fc;">${c.coverage_name}</strong></td>
        <td>$${Number(c.coverage_sum).toLocaleString()}</td>
      </tr>
    `).join('') || '<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 0.6rem;">Standard baseline property coverage (no riders)</td></tr>';

    proofClaimsCount.textContent = `${data.claims?.length || 0} Records`;
    proofClaimsBody.innerHTML = (data.claims || []).map(cl => `
      <tr>
        <td><strong style="color: #fb7185;">${cl.claim_id}</strong></td>
        <td>${cl.policy_id}</td>
        <td>${cl.claim_date}</td>
        <td><strong style="color: #fff;">$${Number(cl.claim_amount_usd).toLocaleString()}</strong></td>
        <td><span class="proof-badge" style="background: ${cl.claim_status.toLowerCase() === 'settled' ? 'rgba(16,185,129,0.2)' : (cl.claim_status.toLowerCase() === 'rejected' ? 'rgba(244,63,94,0.2)' : 'rgba(245,158,11,0.2)')}; color: ${cl.claim_status.toLowerCase() === 'settled' ? '#34d399' : (cl.claim_status.toLowerCase() === 'rejected' ? '#fb7185' : '#fbbf24')};">${cl.claim_status}</span></td>
        <td>${cl.settlement_date}</td>
        <td><span class="proof-badge" style="background: rgba(59,130,246,0.15); color: #60a5fa;">${cl.island_severity_class}</span></td>
      </tr>
    `).join('') || '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 0.6rem;">Clean record: Zero historical claims on file</td></tr>';

    proofPaymentsCount.textContent = `${data.payments?.length || 0} Records`;
    proofPaymentsBody.innerHTML = (data.payments || []).map(py => `
      <tr>
        <td><code>${py.payment_id}</code></td>
        <td>${py.policy_id}</td>
        <td>${py.payment_date}</td>
        <td>$${Number(py.premium_amount_usd).toLocaleString()}</td>
        <td>${py.payment_method}</td>
      </tr>
    `).join('') || '<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 0.6rem;">No payment records recorded</td></tr>';

  } catch (err) {
    proofDemographicsBox.innerHTML = `<div style="color: #fb7185;">Failed to load proof: ${err.message}</div>`;
  }
}

// Accounts Vault (All 120 Accounts Explorer)
async function openAccountsVault() {
  accountsVaultModal.classList.add('active');
  if (allVaultCustomers.length === 0) {
    try {
      const res = await fetch('/api/dataset/customers?filter_type=ALL&limit=120');
      if (res.ok) {
        allVaultCustomers = await res.json();
      }
    } catch (e) {
      console.warn('Error fetching vault accounts:', e);
    }
  }
  filterAndRenderVault();
}

function filterAndRenderVault() {
  const query = (vaultSearchInput?.value || '').trim().toLowerCase();
  let filtered = allVaultCustomers;

  if (activeVaultFilter === 'HIGH_CLAIMS') {
    filtered = filtered.filter(c => c.claim_count >= 2);
  } else if (activeVaultFilter === 'LAPSED') {
    filtered = filtered.filter(c => c.has_lapsed);
  } else if (activeVaultFilter === 'CLEAN') {
    filtered = filtered.filter(c => c.claim_count === 0);
  }

  if (query) {
    filtered = filtered.filter(c => 
      c.customer_id.toLowerCase().includes(query) ||
      c.city.toLowerCase().includes(query) ||
      c.state.toLowerCase().includes(query) ||
      (c.coverages && c.coverages.some(cov => cov.toLowerCase().includes(query)))
    );
  }

  if (vaultRecordCount) {
    vaultRecordCount.textContent = `${filtered.length} of ${allVaultCustomers.length} Accounts`;
  }

  if (!vaultTableBody) return;
  vaultTableBody.innerHTML = filtered.map(c => `
    <tr>
      <td><strong style="color: #60a5fa;">${c.customer_id}</strong></td>
      <td>Age ${c.age}</td>
      <td>${c.city}, ${c.state}</td>
      <td>${c.policy_count} (${c.primary_product_id})</td>
      <td><strong>${c.claim_count}</strong></td>
      <td><strong style="color: ${c.total_claims_amount > 50000 ? '#fb7185' : '#cbd5e1'};">$${Number(c.total_claims_amount).toLocaleString()}</strong></td>
      <td>${c.has_lapsed ? '<span class="proof-badge" style="background: rgba(244,63,94,0.2); color: #fb7185;">Lapsed</span>' : '<span class="proof-badge" style="background: rgba(16,185,129,0.2); color: #34d399;">Active</span>'}</td>
      <td style="font-size: 0.72rem; color: #a78bfa;">${(c.coverages || []).slice(0, 2).join(', ') || 'Standard'}</td>
      <td><span class="proof-badge" style="color: ${c.badge_color === 'rose' ? '#fb7185' : (c.badge_color === 'amber' ? '#fbbf24' : '#34d399')}; background: rgba(255,255,255,0.06);">${c.tag_badge}</span></td>
      <td>
        <div style="display: flex; gap: 0.35rem;">
          <button class="btn-table-action proof-btn" onclick="openCustomerProof('${c.customer_id}')" title="View Source Records">🔬 Proof</button>
          <button class="btn-table-action" onclick="accountsVaultModal.classList.remove('active'); loadAndSynthesizeCustomerId('${c.customer_id}');" title="Synthesize with AI">⚡ Run</button>
        </div>
      </td>
    </tr>
  `).join('') || '<tr><td colspan="10" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">No matching accounts found</td></tr>';
}

// 7. Portfolio Batch Analysis Function
async function runPortfolioBatchAnalysis() {
  portfolioTableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 1.5rem;">Synthesizing portfolio accounts across insurance_model.xlsx...</td></tr>`;

  try {
    const res = await fetch('/api/dataset/batch-evaluate?limit=25', { method: 'POST' });
    if (!res.ok) throw new Error('Portfolio evaluation failed');
    const data = await res.json();

    const dist = data.verdict_distribution || {};
    portApproveCount.textContent = dist['APPROVE'] || 0;
    portConditionalCount.textContent = dist['APPROVE_WITH_CONDITIONS'] || 0;
    portDeclineCount.textContent = (dist['REFER_TO_SENIOR_UW'] || 0) + (dist['DECLINE'] || 0);
    portAvgSpeed.textContent = `Avg Speed: ${data.average_synthesis_time_ms} ms (${data.portfolio_size_evaluated} Accounts)`;

    portfolioTableBody.innerHTML = '';
    (data.customer_summaries || []).forEach(row => {
      const tr = document.createElement('tr');
      let vColor = '#34d399';
      if (row.verdict === 'APPROVE_WITH_CONDITIONS') vColor = '#fbbf24';
      if (row.verdict === 'REFER_TO_SENIOR_UW') vColor = '#fdba74';
      if (row.verdict === 'DECLINE') vColor = '#fb7185';

      tr.innerHTML = `
        <td><strong>${row.customer_id}</strong></td>
        <td>${row.claims}</td>
        <td>$${Number(row.total_claims_amount).toLocaleString()}</td>
        <td><span style="color: ${vColor}; font-weight: 700;">${row.verdict.replace(/_/g, ' ')}</span></td>
        <td>${row.kris_count} Flagged</td>
        <td style="font-family: var(--font-mono);">${row.speed_ms} ms</td>
      `;
      portfolioTableBody.appendChild(tr);
    });
  } catch (err) {
    portfolioTableBody.innerHTML = `<tr><td colspan="6" style="color: #fb7185; text-align: center;">Error running batch: ${err.message}</td></tr>`;
  }
}

// Synchronize What-If sliders with loaded payload
function syncWhatIfSliders(payload) {
  if (payload.policy_request && payload.policy_request.deductible_usd) {
    sliderDeductible.value = payload.policy_request.deductible_usd;
    valDeductible.textContent = `$${Number(payload.policy_request.deductible_usd).toLocaleString()}`;
  }
  if (payload.external_risk_factors && payload.external_risk_factors.environmental_hazard_score !== undefined) {
    sliderHazard.value = payload.external_risk_factors.environmental_hazard_score;
    valHazard.textContent = `${payload.external_risk_factors.environmental_hazard_score}/100`;
  }
}

// 8. Main Synthesis Execution
async function synthesizeRiskProfile() {
  let parsedPayload;

  // If in interactive form tab, ensure latest form values are compiled
  if (activeInputTab === 'tab-form') {
    parsedPayload = buildPayloadFromForm();
    if (jsonEditor) jsonEditor.value = JSON.stringify(parsedPayload, null, 2);
  } else {
    try {
      parsedPayload = JSON.parse(jsonEditor.value);
    } catch (e) {
      showToast('JSON Syntax Error: Please fix formatting in the editor.');
      return;
    }
  }

  // Visual loading state
  const btnIcon = document.getElementById('btnIcon');
  const btnLabel = document.getElementById('btnLabel');
  btnIcon.className = 'spinner';
  btnIcon.textContent = '';
  btnLabel.textContent = 'Synthesizing with GenAI Agent...';
  btnSynthesize.disabled = true;

  const startTime = performance.now();

  try {
    const res = await fetch('/api/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(parsedPayload)
    });

    const elapsed = Math.round(performance.now() - startTime);

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || 'Synthesis failed');
    }

    const report = await res.json();
    latestReport = report;
    renderSynthesisReport(report, elapsed);
    showToast(`Risk profile synthesized in ${report.processing_time_ms || elapsed} ms!`);
  } catch (err) {
    showToast(`Error: ${err.message}`);
  } finally {
    btnIcon.className = '';
    btnIcon.textContent = '⚡';
    btnLabel.textContent = 'Synthesize Risk Profile & KRIs';
    btnSynthesize.disabled = false;
  }
}

// 9. Render Synthesis Output
function renderSynthesisReport(report, clientElapsedMs) {
  // A. Verdict Badge
  verdictBadge.className = 'verdict-pill';
  const v = report.verdict;
  if (v === 'APPROVE') {
    verdictBadge.classList.add('verdict-approve');
    verdictText.textContent = 'APPROVED FOR BINDING';
  } else if (v === 'APPROVE_WITH_CONDITIONS') {
    verdictBadge.classList.add('verdict-approve-conditions');
    verdictText.textContent = 'CONDITIONALLY APPROVED';
  } else if (v === 'REFER_TO_SENIOR_UW') {
    verdictBadge.classList.add('verdict-refer');
    verdictText.textContent = 'REFER TO SENIOR UNDERWRITER';
  } else {
    verdictBadge.classList.add('verdict-decline');
    verdictText.textContent = 'DECLINE PROPOSAL';
  }

  verdictExplanation.textContent = report.verdict_explanation;
  riskTierText.textContent = report.risk_tier.replace('TIER_', 'T-').replace(/_/g, ' ');
  confidenceText.textContent = `${report.confidence_score_pct}%`;
  
  const displayTime = report.processing_time_ms > 0 ? report.processing_time_ms : clientElapsedMs;
  latencyText.textContent = `${displayTime} ms`;

  // B. Executive Narrative
  executiveSummaryText.textContent = report.executive_summary;

  // C. Actuarial Metrics
  const m = report.actuarial_metrics || {};
  valFreq.textContent = m.claim_frequency_annual !== undefined ? m.claim_frequency_annual : '--';
  valSeverity.textContent = m.claim_severity_avg_usd !== undefined ? `$${Number(m.claim_severity_avg_usd).toLocaleString()}` : '--';
  valLossRatio.textContent = m.loss_to_limit_ratio_pct !== undefined ? `${m.loss_to_limit_ratio_pct}%` : '--';
  valHazardScore.textContent = m.hazard_composite_score !== undefined ? `${m.hazard_composite_score}/100` : '--';
  valRiskScore.textContent = m.preliminary_risk_score !== undefined ? `${m.preliminary_risk_score}/100` : '--';

  // D. Key Risk Indicators (KRIs) Showcase Board
  const kris = report.key_risk_indicators || [];
  kriCountBadge.textContent = `${kris.length} Flagged`;
  kriContainer.innerHTML = '';

  if (kris.length === 0) {
    kriContainer.innerHTML = `<div style="text-align: center; color: #34d399; padding: 1.5rem 0;">No adverse risk indicators detected. Account qualifies for preferred baseline terms.</div>`;
  } else {
    kris.forEach(k => {
      const card = document.createElement('div');
      const sevLower = k.severity.toLowerCase();
      card.className = `kri-card severity-${sevLower}`;

      card.innerHTML = `
        <div class="kri-card-header">
          <div class="kri-title-area">
            <span class="kri-code-tag">${k.code}</span>
            <span class="kri-title">${k.title}</span>
          </div>
          <span class="severity-pill ${sevLower}">${k.severity}</span>
        </div>
        <div class="kri-field"><strong>Quantitative Finding:</strong> ${k.quantitative_finding}</div>
        <div class="kri-field"><strong>Underwriting Impact:</strong> ${k.impact_analysis}</div>
        <div class="kri-action-box"><strong>Mitigation / Action:</strong> ${k.recommended_action}</div>
      `;
      kriContainer.appendChild(card);
    });
  }

  // E. Conditions & Endorsements
  conditionsList.innerHTML = '';
  const conditions = report.recommended_conditions || [];
  if (conditions.length === 0) {
    conditionsList.innerHTML = `<li class="condition-item"><span>🔹</span><span>Standard policy conditions apply without mandatory warranty clauses.</span></li>`;
  } else {
    conditions.forEach(cond => {
      const li = document.createElement('li');
      li.className = 'condition-item';
      li.innerHTML = `<span>🔹</span><span>${cond}</span>`;
      conditionsList.appendChild(li);
    });
  }

  if (report.suggested_deductible_adjustment_usd) {
    suggestedDeductibleText.textContent = `$${Number(report.suggested_deductible_adjustment_usd).toLocaleString()}`;
  } else {
    suggestedDeductibleText.textContent = 'Standard Deductible';
  }
}

// 10. Accuracy Benchmark Modal Suite
async function runAccuracyBenchmark() {
  const modalTable = document.getElementById('benchmarkTableBody');
  modalTable.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 1.5rem;">Running automated benchmark suite against actuarial ground truth...</td></tr>`;

  try {
    const res = await fetch('/api/evaluate', { method: 'POST' });
    if (!res.ok) throw new Error('Benchmark evaluation failed');
    const data = await res.json();

    document.getElementById('modalCompositeAccuracy').textContent = `${data.composite_accuracy_pct}%`;
    document.getElementById('modalAvgLatency').textContent = `${(data.average_latency_ms / 1000).toFixed(2)}s`;
    document.getElementById('modalCasesCount').textContent = `${data.total_benchmark_cases} / ${data.total_benchmark_cases}`;

    modalTable.innerHTML = '';
    data.case_breakdowns.forEach(c => {
      const row = document.createElement('tr');
      const matchPill = c.verdict_matched
        ? `<span style="color: #34d399; font-weight: 700;">✔ MATCH</span>`
        : `<span style="color: #fb7185; font-weight: 700;">✘ MISMATCH</span>`;
      row.innerHTML = `
        <td><strong>${c.test_id}</strong><br><span style="color: var(--text-dim); font-size: 0.72rem;">${c.description}</span></td>
        <td><code>${c.expected_verdict}</code></td>
        <td><code>${c.actual_verdict}</code></td>
        <td>${matchPill}</td>
        <td style="font-family: var(--font-mono);">${c.latency_ms} ms</td>
      `;
      modalTable.appendChild(row);
    });
  } catch (err) {
    modalTable.innerHTML = `<tr><td colspan="5" style="color: #fb7185; text-align: center;">Error running benchmark: ${err.message}</td></tr>`;
  }
}

// 11. Event Listeners Setup
function setupEventListeners() {
  btnSynthesize.addEventListener('click', synthesizeRiskProfile);

  if (btnFormatJson) {
    btnFormatJson.addEventListener('click', () => {
      try {
        const obj = JSON.parse(jsonEditor.value);
        jsonEditor.value = JSON.stringify(obj, null, 2);
        showToast('JSON payload formatted.');
      } catch (e) {
        showToast('Invalid JSON: Cannot format.');
      }
    });
  }

  if (btnResetPayload) {
    btnResetPayload.addEventListener('click', () => {
      if (activeScenarioId) {
        selectScenario(activeScenarioId);
        showToast('Reset to scenario original state.');
      }
    });
  }

  // Excel Dataset Filter Buttons
  const filterBtns = document.querySelectorAll('#excelFilterBtns .filter-pill-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      filterExcelCustomers(btn.getAttribute('data-filter'));
    });
  });

  // Customer Select Change
  if (excelCustomerSelect) {
    excelCustomerSelect.addEventListener('change', () => {
      const cid = excelCustomerSelect.value;
      const found = excelCustomers.find(c => c.customer_id === cid);
      updateSelectedStrip(found);
    });
  }

  // Load from Excel Button
  if (btnLoadExcelCustomer) {
    btnLoadExcelCustomer.addEventListener('click', loadAndSynthesizeExcelCustomer);
  }

  // Portfolio Batch Modal Controls
  if (btnOpenPortfolio) {
    btnOpenPortfolio.addEventListener('click', () => {
      portfolioModal.classList.add('active');
      runPortfolioBatchAnalysis();
    });
  }

  if (btnClosePortfolioModal) {
    btnClosePortfolioModal.addEventListener('click', () => {
      portfolioModal.classList.remove('active');
    });
  }

  if (portfolioModal) {
    portfolioModal.addEventListener('click', (e) => {
      if (e.target === portfolioModal) portfolioModal.classList.remove('active');
    });
  }

  // What-If Sliders
  sliderDeductible.addEventListener('input', (e) => {
    valDeductible.textContent = `$${Number(e.target.value).toLocaleString()}`;
    if (formDeductible) formDeductible.value = e.target.value;
  });

  sliderHazard.addEventListener('input', (e) => {
    valHazard.textContent = `${e.target.value}/100`;
    if (formEnvScore) formEnvScore.value = e.target.value;
  });

  btnApplyWhatIf.addEventListener('click', () => {
    try {
      const payload = JSON.parse(jsonEditor.value);
      if (payload.policy_request) {
        payload.policy_request.deductible_usd = Number(sliderDeductible.value);
      }
      if (payload.external_risk_factors) {
        payload.external_risk_factors.environmental_hazard_score = Number(sliderHazard.value);
      }
      jsonEditor.value = JSON.stringify(payload, null, 2);
      populateFormFromPayload(payload);
      showToast('Simulated parameters applied. Re-synthesizing...');
      synthesizeRiskProfile();
    } catch (e) {
      showToast('Please fix JSON formatting first.');
    }
  });

  // Accounts Vault Modal Controls
  btnOpenAccountsVault?.addEventListener('click', openAccountsVault);
  btnOpenVaultFromCard?.addEventListener('click', openAccountsVault);
  btnCloseVaultModal?.addEventListener('click', () => accountsVaultModal.classList.remove('active'));
  accountsVaultModal?.addEventListener('click', (e) => {
    if (e.target === accountsVaultModal) accountsVaultModal.classList.remove('active');
  });
  vaultSearchInput?.addEventListener('input', filterAndRenderVault);

  document.querySelectorAll('.vault-filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.vault-filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeVaultFilter = btn.getAttribute('data-vfilter') || 'ALL';
      filterAndRenderVault();
    });
  });

  // Customer Proof Modal Controls
  btnInspectProofFromCard?.addEventListener('click', () => {
    const custId = excelCustomerSelect ? excelCustomerSelect.value : null;
    if (custId) openCustomerProof(custId);
    else showToast('Please select an account first.');
  });

  btnViewCustomerProof?.addEventListener('click', () => {
    let custId = activeProofCustomerId;
    if (!custId && latestReport) {
      custId = latestReport.customer_id.replace('-EXCEL', '');
    }
    if (!custId && excelCustomerSelect) {
      custId = excelCustomerSelect.value;
    }
    if (custId && custId.startsWith('CUST')) {
      openCustomerProof(custId);
    } else {
      showToast('No Excel relational customer active. Select an account from Excel Explorer.');
    }
  });

  btnCloseProofModal?.addEventListener('click', () => customerProofModal.classList.remove('active'));
  customerProofModal?.addEventListener('click', (e) => {
    if (e.target === customerProofModal) customerProofModal.classList.remove('active');
  });

  btnSynthesizeFromProof?.addEventListener('click', () => {
    if (activeProofCustomerId) {
      customerProofModal.classList.remove('active');
      loadAndSynthesizeCustomerId(activeProofCustomerId);
    }
  });

  // Benchmark Modal Controls
  btnOpenBenchmark.addEventListener('click', () => {
    benchmarkModal.classList.add('active');
    runAccuracyBenchmark();
  });

  btnCloseModal.addEventListener('click', () => {
    benchmarkModal.classList.remove('active');
  });

  btnReRunBenchmark.addEventListener('click', runAccuracyBenchmark);

  benchmarkModal.addEventListener('click', (e) => {
    if (e.target === benchmarkModal) benchmarkModal.classList.remove('active');
  });

  // Copy Executive Memo
  btnCopySummary.addEventListener('click', () => {
    if (!latestReport) {
      showToast('No synthesized report to copy.');
      return;
    }
    const text = `OMNIRISK UNDERWRITING MEMO\n` +
      `Account: ${latestReport.customer_id} | Line: ${latestReport.line_of_business}\n` +
      `Verdict: ${latestReport.verdict} (Confidence: ${latestReport.confidence_score_pct}%)\n\n` +
      `EXECUTIVE SUMMARY:\n${latestReport.executive_summary}\n\n` +
      `KEY RISK INDICATORS:\n` +
      latestReport.key_risk_indicators.map(k => `- [${k.severity}] ${k.title}: ${k.quantitative_finding}`).join('\n') +
      `\n\nCONDITIONS:\n` +
      latestReport.recommended_conditions.map(c => `- ${c}`).join('\n');
    
    navigator.clipboard.writeText(text);
    showToast('Executive Underwriting Memo copied to clipboard!');
  });

  // Export Underwriting Slip
  btnExportSlip.addEventListener('click', () => {
    if (!latestReport) {
      showToast('Synthesize a profile first to export slip.');
      return;
    }
    const blob = new Blob([JSON.stringify(latestReport, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Underwriting_Slip_${latestReport.customer_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Underwriting Slip JSON downloaded.');
  });
}
