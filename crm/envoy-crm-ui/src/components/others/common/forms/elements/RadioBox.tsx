import { Label } from '@apptimus-ui/ui-element';
import React from 'react';

interface Option {
  id: string | number;
  value?: any;
}

interface RadioBoxProps {
  options: Option[];
  selectedValue?: string | number; // <-- string or number
  onChange: (selectedOption: Option) => void;
  name?: string;
  disabled?: boolean;
  className?: string;
  optionClassName?: string;
  isRequired?: boolean;
  label?: string;
}

function RadioBox({ options, selectedValue, onChange, name = 'radio-options', disabled = false, className = '', optionClassName = '', label, isRequired }: RadioBoxProps) {
  const handleRadioChange = (option: Option) => {
    if (disabled) return;
    onChange?.(option);
  };

  return (
    <div className={className}>
      {label && <Label label={label} isRequired={isRequired} />}
      <div>
        {options.map((option: Option) => (
          <label key={option.id} className={`radio-option d-flex align-items-center ${optionClassName} ${disabled ? 'disabled' : ''}`}>
            <input
              type="radio"
              className="form-check-input me-3"
              checked={selectedValue === option.value}
              onChange={() => handleRadioChange(option)}
              disabled={disabled}
              name={name}
              aria-label={`Select ${option.value}`}
            />
            <span className="flex-grow-1 text-muted my-1">{option.value}</span>
          </label>
        ))}
      </div>
    </div>
  );
}

export default RadioBox;
