import S3Avatar from '@/components/others/page-related/S3Avatar';
import React from 'react';

function AssigneeCard({ name, selected }: { name: string; selected: boolean }) {
  return (
    <div className={`d-flex flex-row align-items-center rounded-2 gap-2 border-bottom p-1 ${selected ? 'bg-primary text-white' : ''}`}>
      <div>
        <S3Avatar imageKey={undefined} width={30} height={30} />
      </div>
      <div className="fs-12 fw-medium">{name}</div>
    </div>
  );
}

export default AssigneeCard;
