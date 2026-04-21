import FilterPopup from '@/components/others/FilterPopup';
import { handleFilterInputChange } from '@/helpers/services/commonService';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect } from '@apptimus-ui/select';
import { Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { fetchAllEndorsementTypes } from '../services';

type FilterProps = {
  isOpen: boolean;
  onSubmit: Function;
  onClose: Function;
};

function ReasonFilter({ isOpen, onSubmit, onClose }: FilterProps) {
  const t = useTrans('label.reason');
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
        <div className="mb-3 custom-select">
          <Label label={t('reason_type')} />
          {/* <Select
            onChange={(value) => handleFilterInputChange({ setFilter, key: 'type', value: value, valueType: 'A' })}
            options={reasonTypes}
            option={{ label: 'label', value: 'value' }}
            isSearchable={true}
            multiple
          /> */}
          <AsyncSelect
            onChange={(value) => handleFilterInputChange({ setFilter, key: 'type', value: value, valueType: 'A' })}
            className="form-control error-type_id"
            option={{ label: 'name', value: 'id' }}
            isSearchable={true}
            loadOptions={(searchValue, currentPage) => fetchAllEndorsementTypes(searchValue, currentPage)}
          />
        </div>

        <div className="mb-3">
          <input type="checkbox" onChange={(e) => handleFilterInputChange({ setFilter, key: 'allows_custom_reason', value: e.target.checked ? true : false })} />
          <span className="ms-2 fs-14">{t('allow_custom_reason')}</span>
        </div>
      </FilterPopup>
    </>
  );
}

export default ReasonFilter;
