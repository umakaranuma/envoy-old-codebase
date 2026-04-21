import S3Avatar from '@/components/others/page-related/S3Avatar';
import React from 'react';

function ContactCard({ imageKey = undefined, name }: { imageKey?: string | undefined; name: string }) {
  return (
    <div className={`d-flex flex-row align-items-center rounded-2 gap-1 py-1`}>
      <div>
        <S3Avatar imageKey={imageKey} width={26} height={26} />
      </div>
      <div className="fs-11 fw-medium">{name}</div>
    </div>
  );
}

export default ContactCard;
