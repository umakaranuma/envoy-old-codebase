import { Select } from '@apptimus-ui/select';
import { Label } from '@apptimus-ui/ui-element';
import React from 'react';

function MultiSelectInput({
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
  defaultValue?: string[];
  elementId?: string;
  onChange?: (value: { id: string; value: string }[]) => void;
}) {
  // Map defaultValue (array of string) to array of option objects
  let initialValue: { id: string; value: string }[] = [];
  if (Array.isArray(defaultValue)) {
    initialValue = options.filter((opt) => defaultValue.includes(opt.value));
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
          multiple
        />
      </div>
    </div>
  );
}

export default MultiSelectInput;
