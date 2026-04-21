import React from 'react';
import CreatePolicies from '../_utils/components/create/CreatePolicies';

export default async function Page(props: { searchParams: Promise<{ [key: string]: string | string[] | undefined }> }) {
  const searchParams = await props.searchParams;
  const fromIssuedPolices = searchParams.ip || '';
  const fromValue = fromIssuedPolices === 'true';
  const is_renewal = searchParams.is_renewal === 'true';
  const policy_id = searchParams.policyId?.toString() || '';
  const cusId = searchParams.cusId?.toString() || '';
  const t = searchParams.ct?.toString() || null;
  const leadId = searchParams.leadId?.toString() || '';
  const draftId = searchParams.draftId?.toString() || null;
  const fromReRequest = searchParams.rr?.toString() || null;
  const rr = fromReRequest === 'true';
  return (
    <CreatePolicies
      draftId={draftId}
      fromIssuedPolicies={fromValue}
      customerType={t ? parseInt(t) : null}
      is_renewal={is_renewal}
      policy_base_id={policy_id}
      cusId={cusId}
      leadId={leadId}
      fromReRequest={rr}
    />
  );
}
