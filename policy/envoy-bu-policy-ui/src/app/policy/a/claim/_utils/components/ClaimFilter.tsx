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

function ClaimFilter({ isOpen, onSubmit, onClose }: FilterProps) {
  const t = useTrans('label.sample');
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
          <Input label={t('name')} onChange={(e) => handleFilterInputChange({ setFilter, key: 'name', value: e.target.value })} />
        </div>
        <div className="mb-3">
          <Input label={t('description')} onChange={(e) => handleFilterInputChange({ setFilter, key: 'description', value: e.target.value })} />
        </div>
      </FilterPopup>
    </>
  );
}

export default ClaimFilter;
