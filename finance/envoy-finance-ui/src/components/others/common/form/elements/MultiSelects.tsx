import { Label } from '@apptimus-ui/ui-element';
import React, { useState, useEffect } from 'react';

function MultiSelects({
  onChange,
  options,
  label,
  isRequired,
  className,
  defaultValue = [],
}: {
  onChange: (values: any[]) => void;
  options: any[];
  label?: string;
  isRequired?: boolean;
  className: string;
  defaultValue?: string[];
}) {
  const [selectedOptions, setSelectedOptions] = useState<any[]>([]);

  // Set initial selected options based on defaultValue (array of string values)
  useEffect(() => {
    if (Array.isArray(defaultValue) && defaultValue.length > 0) {
      const initialSelected = options.filter((opt) => defaultValue.includes(opt.value));
      setSelectedOptions(initialSelected);
    }
  }, [defaultValue, options]);

  const handleCheckboxChange = (option: any) => {
    const isSelected = selectedOptions.some((item) => item.value === option.value);
    const newSelection = isSelected ? selectedOptions.filter((item) => item.value !== option.value) : [...selectedOptions, option];

    setSelectedOptions(newSelection);
    onChange?.(newSelection.map((item) => item.value));
  };

  return (
    <div className={`mt-1 ${className}`}>
      {label && <Label label={label} isRequired={isRequired} />}
      {options &&
        options.map((option: any) => (
          <label key={option.value} className="d-flex align-items-center">
            <input
              type="checkbox"
              className="form-check-input me-3"
              checked={selectedOptions.some((item) => item.value === option.value)}
              onChange={() => handleCheckboxChange(option)}
              aria-label={`Select ${option.value}`}
            />
            <span className="flex-grow-1 fw-semibold text-muted my-1">{option.value}</span>
          </label>
        ))}
    </div>
  );
}

export default MultiSelects;
