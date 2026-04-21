import { Input } from '@apptimus-ui/ui-element';
import React, { useState, useEffect } from 'react';

function InputField({
  label,
  isRequired,
  placeholder,
  value,
  onChange,
  type = 'text',
  className,
}: {
  label?: string;
  isRequired?: boolean;
  placeholder?: string;
  value?: any;
  onChange?: (value: string) => void;
  type: any;
  className?: string;
}) {
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
    <Input
      type={type}
      label={label}
      isRequired={isRequired}
      className={className}
      onChange={(event: any) => {
        handleChange(event);
      }}
      value={inputValue}
      placeholder={placeholder}
      rows={5}
    />
  );
}

export default InputField;
