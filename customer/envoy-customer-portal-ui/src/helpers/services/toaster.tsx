import { Flexicon } from '@apptimus-ui/flexicon';
import toast from 'react-hot-toast';

type Position = 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right';
type ToastOptionParam = {
  position?: Position;
};

export const toaster = {
  success: (msg: string, options: ToastOptionParam = { position: 'bottom-left' }) => {
    toast.dismiss();
    return toast(
      (t: any) => (
        <div className="d-flex align-items-start gap-3">
          <span className="text-success">
            <Flexicon icon="check-circle" size={15} />
          </span>
          <div className="d-block" style={{ marginTop: '0.11rem' }}>
            <span className="text-dark fw-semibold fs-16">Success</span>
            <p className="mt-1 fs-15">{msg}</p>
          </div>
          <span className="text-muted pointer" onClick={() => toast.dismiss(t.id)}>
            <Flexicon icon="x-circle" size={15} />
          </span>
        </div>
      ),
      {
        position: options.position,
      },
    );
  },
  error: (msg: string, options: ToastOptionParam = { position: 'bottom-left' }) => toast.error(msg, { position: options.position }),
};
