import React, { useState } from 'react';

function Checkbox({ option, defaultChecked = false, onChange, subLabel = '' }: { option: string; defaultChecked: boolean; onChange: (option: string, checked: boolean) => void; subLabel?: string }) {
  const [isChecked, setIsChecked] = useState(defaultChecked);

  const handleCheckboxChange = () => {
    const newChecked = !isChecked;
    setIsChecked(newChecked);
    if (onChange) {
      onChange(option, newChecked);
    }
  };

  return (
    <div className="form-check p-2">
      <input type="checkbox" className="form-check-input me-2" id={`checkbox-${option || 'default'}`} checked={isChecked} onChange={handleCheckboxChange} aria-label={`Select ${option || 'option'}`} />
      <div>
        <label className="form-check-label" htmlFor={`checkbox-${option || 'default'}`}>
          {option || 'Option'}
        </label>
        {subLabel && <div className="form-text text-muted">{subLabel}</div>}
      </div>
    </div>
  );
}

export default Checkbox;
