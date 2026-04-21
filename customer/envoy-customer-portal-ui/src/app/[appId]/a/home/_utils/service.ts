import { getAllIssuedPolicies, getAllRiskInfoByRiskType, getAllRisksByPolicyBase } from './api-service';

export const howWorksData = [
  {
    step: 1,
    title: 'request_a_quotation',
    description: 'start_by_submitting_a_request_for_a_quotation_for_the_insurance_product_that_fits_your_needs',
  },
  {
    step: 2,
    title: 'confirm_your_quotation',
    description: 'review_the_quotation_details_and_confirm_it_to_proceed_with_the_policy_issuance',
  },
  {
    step: 3,
    title: 'receive_your_policy',
    description: 'once_the_quotation_is_confirmed_your_insurance_policy_will_be_issued_and_made_available_in_your_portal',
  },
  {
    step: 4,
    title: 'manage_your_policy',
    description: 'access_and_manage_your_policy_details_including_payments_coverage_options_and_endorsements',
  },
  {
    step: 5,
    title: 'stay_updated',
    description: 'receive_notifications_and_updates_from_your_insurer_or_broker_to_stay_informed_about_your_policy_status_and_any_upcoming_actions',
  },
];

export async function fetchAllIssuedPolicies(searchValue: any, currentPage: any) {
  const response = await getAllIssuedPolicies({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchOneRiskTypeTableData({ currentPage, itemsPerPage, sortBy, sortDir }: any, riskTypeId: string, customerId: string, policyBaseId?: string) {
  const response = await getAllRiskInfoByRiskType(
    {
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      customer_id: customerId,
      policy_base_id: policyBaseId,
    },
    riskTypeId,
  );

  if (response.is_success) {
    return { data: response.result || [], dataLength: Array.isArray(response.result) ? response.result.length || 0 : 0 };
  }
}

export async function fetchAllRiskTypesByPolicyBase(searchValue: any, currentPage: any, policyBaseId: string) {
  const response = await getAllRisksByPolicyBase({ search: searchValue, page: currentPage }, policyBaseId);

  return response.result || [];
}
