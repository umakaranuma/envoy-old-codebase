import { Skeleton } from '@apptimus-ui/ui-element';

type Style = 'Horizontal' | 'Vertical';

export const Description = ({
  label,
  value,
  style = 'Vertical',
  skeleton = false,
  isHtml = false,
  isTruncate = true,
  isClickable = false,
  onclick,
}: {
  label: string;
  value: any;
  style?: Style;
  skeleton?: boolean;
  isHtml?: boolean;
  isTruncate?: boolean;
  isClickable?: boolean;
  onclick?: () => void;
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
        <div
          className={`${isTruncate ? 'text-truncate' : ''} ${isClickable ? 'pointer text-primary text-decoration-underline' : 'text'}`}
          title={value}
          onClick={isClickable && onclick ? onclick : undefined}
        >
          {value || '-'}
        </div>
      )}
    </div>
  );
};
