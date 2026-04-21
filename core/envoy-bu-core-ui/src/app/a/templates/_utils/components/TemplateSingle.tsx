'use client';
import { useParams } from 'next/navigation';
import React from 'react';

function TemplateSingle() {
  const params = useParams();
  const templateId = params.id?.toString() || '';

  return <div>TemplateSingle{templateId}</div>;
}

export default TemplateSingle;
