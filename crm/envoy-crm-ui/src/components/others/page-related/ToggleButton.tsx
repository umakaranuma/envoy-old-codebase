import React from 'react';

const ToggleButton = ({ isToggled, setIsToggled }: { isToggled: boolean; setIsToggled: Function }) => {
  return (
    <div
      onClick={() => setIsToggled(!isToggled)}
      className={`btn bg-primary ${!isToggled && 'opacity-50'} rounded-5 position-relative border-0`}
      style={{ width: '40px', height: '23px', cursor: 'pointer', transition: 'background-color 0.3s ease' }}
    >
      <div className="bg-white rounded-circle position-absolute" style={{ width: '15px', height: '15px', top: '4px', left: isToggled ? '22px' : '4px', transition: 'left 0.3s ease' }} />
    </div>
  );
};

export default ToggleButton;
