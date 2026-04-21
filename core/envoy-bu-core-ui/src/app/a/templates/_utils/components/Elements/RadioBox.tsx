import { Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';

interface RadioBoxProps {
  options: any[];
  selectedValue?: null;
  onChange: (selectedOption: any) => void;
  name?: string;
  disabled?: boolean;
  className?: string;
  optionClassName?: string;
  isRequired?: boolean;
  label?: string;
}

function RadioBox({ options, selectedValue = null, onChange, name = 'radio-options', disabled = false, className = '', optionClassName = '', label, isRequired }: RadioBoxProps) {
  const [selectedOption, setSelectedOption] = useState<any>(selectedValue);

  const handleRadioChange = (option: any) => {
    if (disabled) return;
    setSelectedOption(option);
    onChange?.(option);
  };

  return (
    <div className={`${className}`}>
      {label && <Label label={label} isRequired={isRequired} />}
      <div>
        {options.map((option: any) => (
          <label key={option.id} className={`radio-option d-flex align-items-center ${optionClassName} ${disabled ? 'disabled' : ''}`}>
            <input
              type="radio"
              className="form-check-input me-3"
              checked={selectedOption?.id === option.id}
              onChange={() => handleRadioChange(option)}
              disabled={disabled}
              name={name}
              aria-label={`Select ${option.label}`}
            />
            <span className="flex-grow-1 text-muted my-1">{option.value}</span>
          </label>
        ))}
      </div>
    </div>
  );
}

export default RadioBox;
