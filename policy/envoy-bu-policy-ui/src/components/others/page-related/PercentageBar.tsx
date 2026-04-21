import React from 'react';

interface RatingProps {
  percentage: number;
}

const PercentageBar: React.FC<RatingProps> = ({ percentage }) => {
  return (
    <div className="d-flex flex-row align-items-center gap-2">
      <div className="progress w-50" style={{ height: '10px' }}>
        <div className="progress-bar bg-primary" role="progressbar" style={{ width: `${percentage}%` }} aria-valuenow={percentage} aria-valuemin={0} aria-valuemax={10}></div>
      </div>
      <div className="text fs-12 ">{percentage}%</div>
    </div>
  );
};

export default PercentageBar;
