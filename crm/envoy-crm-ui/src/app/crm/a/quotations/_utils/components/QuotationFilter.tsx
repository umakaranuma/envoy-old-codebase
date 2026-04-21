import FilterPopup from '@/components/others/FilterPopup';
import { handleFilterInputChange } from '@/helpers/services/commonService';
import { useTrans } from '@/helpers/services/lang/langService';
import { Input } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';

type FilterProps = {
  isOpen: boolean;
  onSubmit: Function;
  onClose: Function;
};

function QuotationFilter({ isOpen, onSubmit, onClose }: FilterProps) {
  const t = useTrans('label.quotations,otr.common');
  const [filter, setFilter] = useState({});

  const onFilterSubmit = () => {
    onSubmit(filter, false);
  };

  const onReset = () => {
    setFilter({});
    onSubmit({}, true);
  };

  return (
    <>
      <FilterPopup {...{ isOpen, onClose, onReset }} onSubmit={() => onFilterSubmit()}>
        <div className="mb-3">
          <Input label={t('quotation_request_id')} onChange={(e) => handleFilterInputChange({ setFilter, key: 'code', value: e.target.value })} />
        </div>
        <div className="mb-3">
          <Input label={t('requested_date')} onChange={(e) => handleFilterInputChange({ setFilter, key: 'requested_date', value: e.target.value })} />
        </div>
      </FilterPopup>
    </>
  );
}

export default QuotationFilter;
