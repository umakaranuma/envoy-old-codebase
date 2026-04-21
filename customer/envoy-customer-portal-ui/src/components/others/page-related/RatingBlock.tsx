import React from 'react';

interface RatingProps {
  value: number;
}

const RatingBlock: React.FC<RatingProps> = ({ value }) => {
  const ratingValue = value === 0 ? 0 : Math.max(1, Math.min(value, 10));

  // Messages based on rating
  const getMessage = (rating: number) => {
    if (rating <= 2) return 'Very Poor';
    if (rating <= 4) return 'Poor';
    if (rating <= 6) return 'Average';
    if (rating <= 8) return 'Good';
    return 'Excellent';
  };

  const getColor = (rating: number) => {
    if (rating <= 2) return 'dark';
    if (rating <= 4) return 'warning';
    if (rating <= 6) return 'info';
    if (rating <= 8) return 'success';
    return 'primary';
  };

  return (
    <div className="d-flex flex-column">
      <div className="d-flex">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((l, index) => (
          <div key={index} className={`px-1 py-1 bg-${ratingValue >= l ? getColor(ratingValue) : 'light'}`} style={{ marginRight: '1px' }}></div>
        ))}
      </div>
      <div className="text fs-13">{getMessage(ratingValue)}</div>
    </div>
  );
};

export default RatingBlock;
