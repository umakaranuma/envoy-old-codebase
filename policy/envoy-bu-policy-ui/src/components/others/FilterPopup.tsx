import { useTrans } from '@/helpers/services/lang/langService';
import { IFilters } from '@/interface/IFilter';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Modal, Size } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import React from 'react';

type FilterProps = {
  isOpen: boolean;
  modelSize?: Size;
  onSubmit: Function;
  onClose: Function;
  onReset: Function;
  children: React.ReactNode;
};

function FilterPopup({ isOpen, modelSize, onSubmit, onClose, onReset, children }: FilterProps) {
  const t = useTrans('otr.common');

  return (
    <>
      <Modal isOpen={isOpen} position="top" {...(modelSize && { size: modelSize })}>
        <div className="column-customize">
          <div className="d-flex justify-content-between align-items-center bg-light p-3">
            <div className="d-flex align-items-center gap-2">
              <Flexicon icon="filter-lines" variant="line" size={18} />
              <h5 className="fs-18 fw-border mb-0">{t('filter')}</h5>
            </div>
            <div className="d-flex align-items-center gap-2">
              <span className="fs-15 text-primary pointer px-2 f-reset-text" onClick={() => onReset()}>
                {t('reset')}
              </span>
              <span className="separationline h-16"></span>
              <span className="d-flex" onClick={() => onClose()}>
                <Flexicon icon="x" variant="line" size={18} className="text-danger pointer" />
              </span>
            </div>
          </div>
          <div className="p-4">
            {children}
            <div className="d-flex gap-2 mt-4">
              <Button text={t('submit')} width="sm" onClick={() => onSubmit({})} />
              <Button text={t('close')} color="light" width="sm" onClick={() => onClose()} />
            </div>
          </div>
        </div>
      </Modal>
    </>
  );
}

export default FilterPopup;

export const getFilterString = (filterData: IFilters) => {
  const formDataObject: IFilters = Object.fromEntries(Object.entries(filterData).filter(([fieldName, value]) => fieldName && value && value.v !== ''));

  return JSON.stringify(formDataObject);
};
