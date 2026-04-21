import React, { useState } from 'react';

type SwitchProps = {
  label?: string;
  isRequired?: boolean;
  className?: string;
  defaultToggled?: boolean;
  onToggle?: (value: boolean) => void;
};

function Switch({ label, isRequired, className, defaultToggled = false, onToggle }: SwitchProps) {
  const [isToggled, setIsToggled] = useState(defaultToggled);

  const toggle = () => {
    const newState = !isToggled;
    setIsToggled(newState);
    onToggle?.(newState);
  };

  return (
    <div className={`mt-2 ${className}`}>
      {label && (
        <div className="text-muted">
          {label}
          {isRequired && <span className="text-danger">*</span>}
        </div>
      )}
      <div
        role="switch"
        aria-checked={isToggled}
        tabIndex={0}
        onClick={toggle}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggle();
          }
        }}
        className={`btn mt-2 bg-primary ${!isToggled && 'opacity-50'} rounded-5 position-relative border-0`}
        style={{
          width: '40px',
          height: '23px',
          cursor: 'pointer',
          transition: 'background-color 0.3s ease',
        }}
      >
        <div
          className="bg-white rounded-circle position-absolute"
          style={{
            width: '15px',
            height: '15px',
            top: '4px',
            left: isToggled ? '22px' : '4px',
            transition: 'left 0.3s ease',
          }}
        />
      </div>
    </div>
  );
}

export default Switch;
