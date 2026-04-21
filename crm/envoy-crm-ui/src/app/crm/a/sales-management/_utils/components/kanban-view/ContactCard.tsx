import S3Avatar from '@/components/others/page-related/S3Avatar';
import React from 'react';

function ContactCard({ imageKey = undefined, name, email }: { imageKey?: string | undefined; name: string; email: string }) {
  return (
    <div className={`d-flex flex-row align-items-center rounded-2 gap-1`}>
      <div>
        <S3Avatar imageKey={imageKey} width={35} height={35} />
      </div>
      <div>
        <div className="fs-11 fw-medium">{name}</div>
        <div className="fs-10">{email}</div>
      </div>
    </div>
  );
}

export default ContactCard;
