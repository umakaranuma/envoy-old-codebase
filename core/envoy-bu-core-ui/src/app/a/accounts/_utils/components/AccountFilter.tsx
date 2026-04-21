import FilterPopup from '@/components/others/FilterPopup';
import { handleFilterInputChange } from '@/helpers/services/commonService';
import { useTrans } from '@/helpers/services/lang/langService';
import { Select } from '@apptimus-ui/select';
import { Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';

type FilterProps = {
  isOpen: boolean;
  onSubmit: Function;
  onClose: Function;
};

function AccountFilter({ isOpen, onSubmit, onClose }: FilterProps) {
  const t = useTrans('label.accounts');
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
          <Label label={t('account_type')} />
          <Select
            onChange={(value) => handleFilterInputChange({ setFilter, key: 'type', value: value, valueType: 'A' })}
            options={[
              { label: t('corporate'), value: 'Corporate' },
              { label: t('personal'), value: 'Personal' },
            ]}
            option={{ label: 'label', value: 'value' }}
            isSearchable={false}
            multiple
          />
        </div>
      </FilterPopup>
    </>
  );
}

export default AccountFilter;
