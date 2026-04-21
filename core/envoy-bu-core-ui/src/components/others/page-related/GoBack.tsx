import { Skeleton } from '@apptimus-ui/ui-element';
import React from 'react';

function GoBack({ goTo, title, skeleton }: { goTo: Function; title?: string; skeleton?: boolean }) {
  return (
    <>
      <div className="d-flex align-items-center gap-2 mb-4 page-go-back">
        <div className="back-custom-arrow-btn rounded-circle pointer me-1" onClick={() => goTo()}>
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        {!skeleton ? <div className="fs-title fw-medium ms-2">{title}</div> : <Skeleton height="24px" width="200px" />}
      </div>
    </>
  );
}

export default GoBack;
