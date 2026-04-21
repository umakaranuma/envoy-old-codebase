import { Label } from '@apptimus-ui/ui-element';
import React, { useState, useEffect } from 'react';

const FilledStar = ({ size = 24, color = 'gold' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={color}>
    <polygon points="12,2 15,9 22,9 17,14 18,21 12,17 6,21 7,14 2,9 9,9" />
  </svg>
);

const EmptyStar = ({ size = 24, color = 'gold' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2">
    <polygon points="12,2 15,9 22,9 17,14 18,21 12,17 6,21 7,14 2,9 9,9" />
  </svg>
);

interface StarRatingDisplayProps {
  value: number;
  onChange?: (value: number) => void;
  interactive?: boolean;
  label?: string;
  color?: string;
  isRequired?: boolean;
  className?: string;
  id: any;
}

const StarRatingDisplay: React.FC<StarRatingDisplayProps> = ({ value, onChange, interactive = true, label, color = 'gold', isRequired, className, id }) => {
  const [currentValue, setCurrentValue] = useState<number>(value);
  const [hoverValue, setHoverValue] = useState<number | null>(null);

  useEffect(() => {
    setCurrentValue(value);
  }, [value]);

  const handleClick = (newValue: number) => {
    if (interactive) {
      setCurrentValue(newValue);
      onChange?.(newValue);
    }
  };

  return (
    <div id={id} className={className}>
      {label && <Label label={label} isRequired={isRequired} />}
      <div
        role={interactive ? 'slider' : undefined}
        aria-valuenow={currentValue}
        aria-valuemin={1}
        aria-valuemax={5}
        aria-label={interactive ? 'Star rating' : 'Star rating display'}
        aria-readonly={!interactive}
        className="d-flex gap-2"
      >
        {[...Array(5)].map((_, index) => {
          const starValue = index + 1;
          const isFilled = starValue <= (hoverValue ?? currentValue);

          return (
            <button
              key={starValue}
              type="button"
              className="star-button p-0 bg-transparent border-0"
              onClick={() => handleClick(starValue)}
              onMouseEnter={() => interactive && setHoverValue(starValue)}
              onMouseLeave={() => interactive && setHoverValue(null)}
              disabled={!interactive}
              aria-label={`Rate ${starValue} out of 5`}
              style={{ cursor: interactive ? 'pointer' : 'default' }}
            >
              {isFilled ? <FilledStar size={45} color={color} /> : <EmptyStar size={45} color={color} />}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default StarRatingDisplay;
