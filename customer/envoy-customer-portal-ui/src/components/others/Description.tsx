import { Skeleton } from '@apptimus-ui/ui-element';

type Style = 'Horizontal' | 'Vertical';

export const Description = ({
  label,
  value,
  style = 'Vertical',
  skeleton = false,
  isHtml = false,
  isTruncate = true,
}: {
  label: string;
  value: any;
  style?: Style;
  skeleton?: boolean;
  isHtml?: boolean;
  isTruncate?: boolean;
}) => {
  return (
    <div className={`custom-description ${style}`}>
      <div className="text-muted">
        {label} {style === 'Horizontal' ? ':' : ''}{' '}
      </div>
      {skeleton ? (
        <Skeleton width={'65%'} height={'24px'} />
      ) : isHtml ? (
        <div className="text-truncate text" dangerouslySetInnerHTML={{ __html: value || '' }}></div>
      ) : (
        <div className={`${isTruncate ? 'text-truncate text' : ''}`} title={value}>
          {value || '-'}
        </div>
      )}
    </div>
  );
};
