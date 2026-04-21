import React from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Badge } from '@apptimus-ui/ui-element';
import S3Avatar from '@/components/others/page-related/S3Avatar';

function PolicyCard({
  picture,
  name,
  contactNumber,
  contactEmail,
  productName,
  policyNumber,
  riskType,
}: {
  picture?: string;
  name: string;
  contactNumber?: string;
  contactEmail?: string;
  productName?: string;
  policyNumber?: string;
  riskType?: string;
}) {
  return (
    <div className="text d-flex align-items-center gap-2 p-1">
      <S3Avatar imageKey={picture || ''} width={40} height={40} className="m-1" />
      <div>
        <div className="d-flex flex-row gap-2">
          {productName}
          {/* <Badge text={policyNumber} variant='outline' color='primary' radius='pill' /> */}
          <Badge text={riskType} variant="light" color="secondary" />
          {/* <Badge text={productName} variant='light' color='success' radius='pill' /> */}
        </div>
        <div className="text-muted mt-1">
          <div className="d-flex flex-row gap-2">
            {name}
            <Badge text={policyNumber} variant="outline" color="primary" radius="pill" />
          </div>
          <Flexicon icon="phone" variant="line" size={14} className="text-primary me-1" />
          <span className="fs-12">{contactNumber || '-'}</span>
          <span className="fs-12"> | </span>
          <Flexicon icon="mail-01" variant="line" size={14} className="text-primary me-1" />
          <span className="fs-12">{contactEmail || '-'}</span>
        </div>
      </div>
    </div>
  );
}

export default PolicyCard;
