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

function RolesFilter({ isOpen, onSubmit, onClose }: FilterProps) {
  const t = useTrans('label.role');
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
          <Input label={t('role_name')} onChange={(e) => handleFilterInputChange({ setFilter, key: 'role_name', value: e.target.value })} />
        </div>
        <div className="mb-3">
          <Input label={t('description')} onChange={(e) => handleFilterInputChange({ setFilter, key: 'description', value: e.target.value })} />
        </div>
        <div className="mb-3">
          <Input label={t('number_of_privileges')} onChange={(e) => handleFilterInputChange({ setFilter, key: 'number_of_privileges', value: e.target.value })} />
        </div>
      </FilterPopup>
    </>
  );
}

export default RolesFilter;
