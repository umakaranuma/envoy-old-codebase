import React from 'react';

interface CustomBadgeProps {
  text: string;
  color: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'light' | 'dark';
}

function CustomBadge({ text, color }: CustomBadgeProps) {
  return (
    <div className={`d-flex flex-row align-items-center gap-1 rounded-1 bg-${color} bg-opacity-10 border border-${color} fs-10 fw-bold text-${color} custom-badge`}>
      <svg width="9" height="8" viewBox="0 0 9 8" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="4.375" cy="4" r="3" fill={getColor(color)} />
      </svg>
      {text}
    </div>
  );
}

const getColor = (color: string) => {
  const colorMap: { [key: string]: string } = {
    primary: '#0D6EFD',
    secondary: '#6C757D',
    success: '#198754',
    danger: '#DC3545',
    warning: '#FFC107',
    info: '#0DCAF0',
    light: '#F8F9FA',
    dark: '#212529',
  };
  return colorMap[color] || '#000';
};

export default CustomBadge;
