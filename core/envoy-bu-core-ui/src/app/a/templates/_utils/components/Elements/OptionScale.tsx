import { Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';

type OptionScaleProps = {
  onChange?: (value: number) => void;
  label?: string;
  isRequired?: boolean;
  className?: string;
  value?: number; // selected value only (1–10)
};

const OptionScale: React.FC<OptionScaleProps> = ({
  onChange,
  label,
  isRequired,
  className,
  value = 5, // default selected value
}) => {
  const [selected, setSelected] = useState<number>(value);

  const handleClick = (val: number) => {
    setSelected(val);
    onChange?.(val);
  };

  useEffect(() => {
    if (value !== undefined) {
      setSelected(value);
    }
  }, [value]);

  return (
    <div className={className}>
      {label && <Label label={label} isRequired={isRequired} />}
      <div className="d-flex gap-2 flex-wrap rounded-3">
        {Array.from({ length: 10 }, (_, i) => (
          <div
            key={i}
            className={`rounded-3 d-flex justify-content-center align-items-center text-white ${i < selected ? 'bg-primary' : 'border border-1 border-primary text'}`}
            style={{ width: '30px', height: '30px', cursor: 'pointer' }}
            onClick={() => handleClick(i + 1)}
          >
            {i + 1}
          </div>
        ))}
      </div>
    </div>
  );
};

export default OptionScale;
