import React from 'react';
import IdpCallback from './_utilities/components/IdpCallback';
async function Page(props: { searchParams: Promise<{ [key: string]: string | string[] | undefined }> }) {
  const searchParams = await props.searchParams;
  const invitation = searchParams.invitation;
  const token = searchParams.access_token || '';
  return <IdpCallback invitation={invitation as string} token={token as string} />;
}

export default Page;
