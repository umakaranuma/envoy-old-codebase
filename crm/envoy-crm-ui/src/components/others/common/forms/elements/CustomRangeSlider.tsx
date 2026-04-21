'use client';

import React, { useState, useEffect } from 'react';
import { Label } from '@apptimus-ui/ui-element';

interface CustomRangeSliderProps {
  min?: number;
  max?: number;
  step?: number;
  onChange?: (value: number) => void;
  label?: string;
  isRequired?: boolean;
  className?: string;
  value?: number;
}

const CustomRangeSlider: React.FC<CustomRangeSliderProps> = ({ value, min = 0, max = 100, step = 1, onChange, isRequired, label, className }) => {
  const [sliderValue, setSliderValue] = useState<number>(value ?? min);

  useEffect(() => {
    if (value !== undefined) {
      setSliderValue(value);
    }
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = Number(e.target.value);
    setSliderValue(newValue);
    if (onChange) onChange(newValue);
  };

  const percentage = ((sliderValue - min) / (max - min)) * 100;

  return (
    <div className={className}>
      <div className="d-flex justify-content-between mt-2">
        <div>{label ? <Label label={label} isRequired={isRequired} /> : <div />}</div>
        <div className="fw-semibold">
          {sliderValue}/{max}
        </div>
      </div>
      <input type="range" className="slider" value={sliderValue} min={min} max={max} step={step} onChange={handleChange} style={{ '--slider-percentage': `${percentage}%` } as React.CSSProperties} />
    </div>
  );
};

export default CustomRangeSlider;
