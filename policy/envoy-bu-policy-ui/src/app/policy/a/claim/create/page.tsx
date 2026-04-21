import React from 'react';
import { ClaimCreate } from '../_utils/components/claim-create/ClaimCreate';

async function page(props: { searchParams: Promise<{ [key: string]: string | string[] }> }) {
  const searchParams = await props.searchParams;
  const policyId = searchParams.pid.toString() || '';
  const riskId = searchParams.rid.toString() || '';
  const infoId = searchParams.infoId.toString() || '';
  return <ClaimCreate policyId={policyId} riskId={riskId} infoId={infoId} />;
}

export default page;
