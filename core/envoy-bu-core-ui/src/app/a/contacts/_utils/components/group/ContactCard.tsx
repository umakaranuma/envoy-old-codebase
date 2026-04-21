import S3Avatar from '@/components/others/page-related/S3Avatar';
import React from 'react';

function ContactCard({ name, email, contactNumber }: { email: string; name: string; contactNumber: string }) {
  return (
    <div className="d-flex flex-row align-items-center gap-2">
      <div>
        <S3Avatar imageKey={undefined} width={50} height={50} />
      </div>
      <div className="d-flex flex-column">
        <div className="fw-medium">{name}</div>
        <div className="fs-12">{email}</div>
        <div className="fs-11">{contactNumber}</div>
      </div>
    </div>
  );
}

export default ContactCard;
