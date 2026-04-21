import { Select } from '@apptimus-ui/select';
import { Label } from '@apptimus-ui/ui-element';
import React from 'react';

function SelectInput({
  label,
  isRequired,
  options,
  defaultValue,
  elementId,
  onChange,
}: {
  label?: string;
  isRequired?: boolean;
  options: { id: string; value: string }[];
  defaultValue?: string;
  elementId?: string;
  onChange?: (value: { id: string; value: string }) => void;
}) {
  // If defaultValue is a string, search for the option with matching value
  let initialValue: { id: string; value: string } | undefined = undefined;
  if (typeof defaultValue === 'string') {
    initialValue = options.find((opt) => opt.value === defaultValue);
  }

  return (
    <div>
      {label && <Label label={label} isRequired={isRequired} />}
      <div>
        <Select
          options={options}
          defaultValue={initialValue}
          option={{ label: 'value', value: 'id' }}
          onChange={(_, data) => {
            if (onChange) onChange(data);
          }}
          className={`error-${elementId}`}
        />
      </div>
    </div>
  );
}

export default SelectInput;
