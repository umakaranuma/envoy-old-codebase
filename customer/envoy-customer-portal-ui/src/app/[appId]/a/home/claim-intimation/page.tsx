import React from 'react';
import { ClaimIntimation } from '../_utils/components/claim-intimation/ClaimIntimation';

async function Page(props: { searchParams: Promise<{ [key: string]: string | string[] | undefined }> }) {
  const searchParams = await props.searchParams;
  const policyId = searchParams.pid as string;
  const rIds = searchParams.rIds as string;
  return <ClaimIntimation policyId={policyId} riskInfoIds={rIds} />;
}

export default Page;
