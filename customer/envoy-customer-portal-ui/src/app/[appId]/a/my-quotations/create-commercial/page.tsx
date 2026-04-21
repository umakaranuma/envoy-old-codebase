import React from 'react';
import CreateCommercialLineQuotation from '../_utils/components/CreateCommercialLineQuotation';

async function page(props: { searchParams: Promise<{ [key: string]: string | string[] | undefined }> }) {
  const searchParams = await props.searchParams;
  const reqId = searchParams.reqId as string;
  const pId = searchParams.pId as string;
  const rId = searchParams.rId as string;
  return <CreateCommercialLineQuotation productId={pId} riskTypeId={rId} requestId={reqId} />;
}

export default page;
