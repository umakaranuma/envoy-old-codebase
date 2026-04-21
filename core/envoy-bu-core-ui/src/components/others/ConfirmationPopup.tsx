import { useTrans } from '@/helpers/services/lang/langService';
import { Modal } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';

export const ConfirmationPopup = (props: {
  isOpen: boolean;
  onYes: Function;
  onCancel: Function;
  msg?: string;
  yesButtonLabel?: string;
  noButtonLabel?: string;
  isFormProcessing?: boolean;
  position?: 'top' | 'center';
}) => {
  const t = useTrans('otr.common');
  const { msg = t('default_confirmation_msg'), yesButtonLabel = t('yes'), noButtonLabel = t('no'), isOpen, onYes, onCancel, isFormProcessing = false, position = 'top' } = props;

  return (
    <>
      <Modal isOpen={isOpen} position={position}>
        <p className="px-3 mt-4 text-start">{msg}</p>
        <div className="d-flex justify-content-start mt-2 gap-2 px-3 pb-4">
          <Button text={yesButtonLabel} size="sm" width="sm" onClick={() => onYes()} isLoading={isFormProcessing} />
          <Button text={noButtonLabel} color="light" size="sm" width="sm" onClick={() => onCancel()} />
        </div>
      </Modal>
    </>
  );
};
