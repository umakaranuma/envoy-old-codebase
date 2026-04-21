'use client';
import React from 'react';
import WithInvitation from './WithInvitation';
import WithoutInvitation from './WithoutInvitation';

function IdpCallback({ invitation, token }: { invitation?: string; token: string }) {
  return <div className="vh-100 d-flex justify-content-center align-items-center">{invitation ? <WithInvitation invitation={invitation} token={token} /> : <WithoutInvitation token={token} />}</div>;
}

export default IdpCallback;
