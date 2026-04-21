import { Skeleton } from '@apptimus-ui/ui-element';
import Image from 'next/image';
import { useEffect, useState } from 'react';
import defaultImage from '../../../../public/images/empty-avatar.png';

function S3Avatar({
  imageKey,
  width = 40,
  height = 40,
  className = 'rounded-circle border border-2 me-2',
  loading = false,
  style,
  layout,
}: {
  imageKey: string | undefined;
  height?: number;
  width?: number;
  className?: string;
  loading?: boolean;
  style?: React.CSSProperties;
  layout?: string;
}) {
  if (!imageKey || imageKey.length === 0) {
    return <Image src={defaultImage} alt="no-image" width={width} height={height} className={`${className}`} style={style} />;
  }

  const [waiting, setWaiting] = useState(true);

  useEffect(() => {
    const handler = setTimeout(() => {
      setWaiting(false);
    }, 500);
    return () => {
      clearTimeout(handler);
    };
  }, []);
  return (
    <div>
      {!loading || !waiting ? (
        <Image src={`${process.env.S3CDN}/${imageKey}`} height={height} width={width} loading="lazy" className={`${className}`} alt="Image" style={style} layout={layout} />
      ) : (
        <Skeleton height={`${height}px`} width={`${width}px`} className={className} />
      )}
    </div>
  );
}

export default S3Avatar;
