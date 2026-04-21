import { Skeleton } from '@apptimus-ui/ui-element';
import Image from 'next/image';
import { useEffect, useState } from 'react';
import defaultImage from '../../../../public/images/empty-avatar.png';

interface ProfileInfoProps {
  imageKey?: string | null;
  width?: number;
  height?: number;
  imgClassName?: string;
  containerClassName?: string;
  loading?: boolean;
  title?: string;
  subtitle?: string;
  titleClassName?: string;
  subtitleClassName?: string;
  shape?: 'circle' | 'square';
  defaultImage?: string;
}

function ProfileInfo({
  imageKey,
  width = 35,
  height = 35,
  imgClassName = '',
  containerClassName = '',
  loading = false,
  title,
  subtitle,
  titleClassName = '',
  subtitleClassName = 'text-muted small',
  shape = 'circle',
  defaultImage: customDefaultImage,
}: ProfileInfoProps) {
  const [imgError, setImgError] = useState(false);
  const [waiting, setWaiting] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setWaiting(false), 500);
    return () => clearTimeout(timer);
  }, []);

  // Determine the image source
  const imageSrc = imgError || !imageKey ? customDefaultImage || defaultImage : `${process.env.S3CDN}/${imageKey}`;

  // Build the className based on shape and user provided className
  const finalImgClassName = `${imgClassName} ${shape === 'circle' ? 'rounded-circle' : 'rounded'} me-2`.trim();

  return (
    <div className={`d-flex align-items-center ${containerClassName}`}>
      <div style={{ width: width, height: height, flexShrink: 0 }}>
        {!loading && !waiting ? (
          <Image
            src={imageSrc}
            alt={title || 'Profile image'}
            width={width}
            height={height}
            className={finalImgClassName}
            onError={() => setImgError(true)}
            loading="lazy"
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
        ) : (
          <Skeleton height={`${height}px`} width={`${width}px`} className={finalImgClassName} />
        )}
      </div>

      {(title || subtitle) && (
        <div className="d-flex flex-column ms-2">
          {title && <span className={titleClassName}>{title}</span>}
          {subtitle && <span className={subtitleClassName}>{subtitle}</span>}
        </div>
      )}
    </div>
  );
}

export default ProfileInfo;
