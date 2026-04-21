import React from 'react';
import S3Avatar from './S3Avatar';
import { Flexicon } from '@apptimus-ui/flexicon';

function CustomerCard({ picture, name, contactNumber, contactEmail }: { picture?: string; name: string; contactNumber?: string; contactEmail?: string }) {
  return (
    <div className="text d-flex align-items-center gap-2">
      <S3Avatar imageKey={picture || ''} width={40} height={40} className="m-1" />
      <div>
        <div>{name}</div>
        <div className="text-muted">
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

export default CustomerCard;
