import { cashFlowStatements, chartOfAccounts, commissionEarned, commissionGiven, debtorAgingSummaryReport, generalLedger, journalEntries, policyMade, salesReport } from './api-service';

export async function fetchChartOfAccountsTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await chartOfAccounts(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
    },
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchCashFlowStatementsTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await cashFlowStatements(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
    },
    true,
  );
  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchJournalEntriesTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await journalEntries(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
    },
    true,
  );
  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchGeneralLedgerTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await generalLedger(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
    },
    true,
  );
  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchDebtorAgingSummaryReportTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await debtorAgingSummaryReport(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
    },
    true,
  );
  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchCommissionEarnedTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await commissionEarned(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
    },
    true,
  );
  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchCommissionGivenTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await commissionGiven(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
    },
    true,
  );
  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchPolicyMadeTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await policyMade(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
    },
    true,
  );
  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchSalesReportTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await salesReport(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
    },
    true,
  );
  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllSampleData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await salesReport(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
    },
    true,
  );
  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}
