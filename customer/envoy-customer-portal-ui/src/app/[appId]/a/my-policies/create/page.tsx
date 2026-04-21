import React from 'react';
import Create from '../_utils/components/create-policy/individual/Create';

async function Page(props: { searchParams: Promise<{ [key: string]: string | string[] | undefined }> }) {
  const searchParams = await props.searchParams;
  const fId = searchParams.fId as string;
  const pId = searchParams.pId as string;
  const rId = searchParams.rId as string;
  return <Create formId={fId} productId={pId} riskTypeId={rId} />;
}

export default Page;
