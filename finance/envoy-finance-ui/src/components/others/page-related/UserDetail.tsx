import React from 'react';
import Image from 'next/image';

interface UserDetailProps {
  title?: string;
  subtitle?: string;
  imageUrl?: string;
  size?: number;
  compact?: boolean;
  className?: string;
  type?: 'circle' | 'square';
}

function UserDetail({ title, subtitle, imageUrl, size = 32, compact = false, className = '', type = 'circle' }: UserDetailProps) {
  const shapeClass = type === 'circle' ? 'rounded-circle' : type === 'square' ? 'rounded-3' : '';

  return (
    <div className={`d-flex align-items-center gap-2 ${className}`}>
      <Image src={imageUrl || '/images/avatar.jpg'} alt={title || 'User'} width={size} height={size} className={shapeClass} />
      <div>
        {title && <div>{title}</div>}
        {!compact && subtitle && <div className="text-muted">{subtitle}</div>}
      </div>
    </div>
  );
}

export default UserDetail;
