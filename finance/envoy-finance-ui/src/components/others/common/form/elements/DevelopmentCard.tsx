import React from 'react';

const DevelopmentCard: React.FC<{ label?: string }> = ({ label }) => (
  <div className="card w-100 my-3 shadow-sm bg-white">
    <div className="card-body text-center">
      <h5 className="card-title text-warning mb-2">{label || 'This feature is under development'}</h5>
      <p className="card-text text-secondary">Please check back later.</p>
    </div>
  </div>
);

export default DevelopmentCard;
