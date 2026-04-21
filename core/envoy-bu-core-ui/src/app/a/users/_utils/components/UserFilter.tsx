import FilterPopup from '@/components/others/FilterPopup';
import { handleFilterInputChange } from '@/helpers/services/commonService';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect } from '@apptimus-ui/select';
import { Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { getAllRoles } from '../service';

type FilterProps = {
  isOpen: boolean;
  onSubmit: Function;
  onClose: Function;
};

function UserFilter({ isOpen, onSubmit, onClose }: FilterProps) {
  const t = useTrans('label.user');
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
          <Label label={t('role')} />
          <AsyncSelect
            onChange={(value: any) => {
              handleFilterInputChange({ setFilter, key: 'role_id', value: value, valueType: 'A' });
            }}
            option={{
              label: 'name',
              value: 'id',
            }}
            loadOptions={(searchValue, currentPage) => getAllRoles(searchValue, currentPage)}
            multiple
          />
        </div>
      </FilterPopup>
    </>
  );
}

export default UserFilter;
