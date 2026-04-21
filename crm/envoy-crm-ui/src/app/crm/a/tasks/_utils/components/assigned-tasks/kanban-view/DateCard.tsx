import { Flexicon } from '@apptimus-ui/flexicon';
import React from 'react';

function DateCard({ dateType, date }: { dateType: string; date: string }) {
  return (
    <div className="mt-2">
      <div className="fs-13">{dateType}</div>
      <div className="d-flex flex-row align-items-center gap-2">
        {date ? (
          <div className="d-flex align-items-center gap-2 text-muted mt-2">
            <Flexicon icon="calendar" variant="line" size={16} />
            <div className="text-muted fs-13">{date}</div>
          </div>
        ) : (
          <div className="text">-</div>
        )}
      </div>
    </div>
  );
}

export default DateCard;
