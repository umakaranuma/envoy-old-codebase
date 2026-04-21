import React, { useState, useEffect } from 'react';
import { Icons } from './Icons';
import { Label } from '@apptimus-ui/ui-element';

interface IconInputProps {
  id?: any;
  placeholder?: string;
  error?: boolean;
  icon: string;
  onChange?: (value: string) => void;
  type?: string;
  value?: string;
  className?: string;
  isRequired?: boolean;
  label?: string;
}

const IconInput: React.FC<IconInputProps> = ({ id, placeholder, icon, onChange, type = 'text', value, className = '', isRequired, label }) => {
  const [inputValue, setInputValue] = useState(value || '');

  useEffect(() => {
    if (value !== undefined && value !== inputValue) {
      setInputValue(value);
    }
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    if (onChange) {
      onChange(newValue);
    }
  };

  return (
    <>
      {label && <Label label={label} isRequired={isRequired} />}
      <div className={`input-group`}>
        {<span className="input-group-text">{<Icons icon={icon} />}</span>}
        <input type={type} id={id} className={`form-control ${className} `} placeholder={placeholder} onChange={handleChange} value={inputValue} required={isRequired} />
      </div>
    </>
  );
};

export default IconInput;
