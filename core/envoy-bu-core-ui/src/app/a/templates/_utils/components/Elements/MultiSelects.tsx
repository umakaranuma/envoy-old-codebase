import { Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';

function MultiSelects({ onChange, options, label, isRequired, className }: { onChange: any; options: any; label?: string; isRequired?: boolean; className: string }) {
  const [selectedOptions, setSelectedOptions] = useState<any[]>([]);

  const handleCheckboxChange = (option: any) => {
    const isSelected = selectedOptions.some((item) => item.id === option.id);
    const newSelection = isSelected ? selectedOptions.filter((item) => item.id !== option.id) : [...selectedOptions, option];

    setSelectedOptions(newSelection);
    onChange?.(newSelection);
  };

  return (
    <div className={`mt-1` + className}>
      {label && <Label label={label} isRequired={isRequired} />}
      {options &&
        options.map((option: any) => (
          <label key={option.id} className="d-flex align-items-center">
            <input
              type="checkbox"
              className="form-check-input me-3"
              checked={selectedOptions.some((item) => item.id === option.id)}
              onChange={() => handleCheckboxChange(option)}
              aria-label={`Select ${option.option_value}`}
            />
            <span className="flex-grow-1 text-muted my-1">{option.value}</span>
          </label>
        ))}
    </div>
  );
}

export default MultiSelects;
