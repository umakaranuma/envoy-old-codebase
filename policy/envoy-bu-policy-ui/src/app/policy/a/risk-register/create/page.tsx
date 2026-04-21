import React from 'react';
import CreateRiskRegister from '../_utils/components/CreateRiskRegister';

async function page(props: { searchParams: Promise<{ [key: string]: string | string[] | undefined }> }) {
  const searchParams = await props.searchParams;
  const customerId = searchParams.cId?.toString() || '';
  const leadId = searchParams.lId?.toString() || '';
  const riskId = searchParams.rId?.toString() || '';

  return <CreateRiskRegister customerId={customerId} leadId={leadId} riskId={riskId} />;
}

export default page;
