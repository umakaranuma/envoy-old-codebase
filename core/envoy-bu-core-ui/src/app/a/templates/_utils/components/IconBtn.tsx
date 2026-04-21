import React from 'react';

interface IconBtnProps {
  icon?: React.ReactNode;
  title: string;
  onClick?: () => void;
}

function IconBtn({ icon, title, onClick }: IconBtnProps) {
  return (
    <button className="bg-white p-1 rounded-2 h-100 d-flex flex-column align-items-center border-0 hover-shadow" style={{ width: '50px', minHeight: '60px', cursor: 'pointer' }} onClick={onClick}>
      <div className="bg-primary rounded-2 p-2 mb-1 d-flex align-items-center justify-content-center " style={{ width: '32px', height: '32px' }}>
        {icon}
      </div>
      <div className="fw-medium text-center fs-8 text">{title}</div>
    </button>
  );
}

export default IconBtn;
