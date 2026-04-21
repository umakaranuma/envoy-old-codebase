import FilterPopup from '@/components/others/FilterPopup';
import { handleFilterInputChange } from '@/helpers/services/commonService';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect } from '@apptimus-ui/select';
import { Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { fetchAllOpportunityStages, fetchAllTaskTypes } from '../../service';

type FilterProps = {
  isOpen: boolean;
  onSubmit: Function;
  onClose: Function;
};

function TaskConfigFilter({ isOpen, onSubmit, onClose }: FilterProps) {
  const t = useTrans('label.general_settings');
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
          <Label label={t('task_type')} />
          <AsyncSelect onChange={(value: any) => handleFilterInputChange({ setFilter, key: 'task_type_id', value: value, valueType: 'A' })} loadOptions={fetchAllTaskTypes} multiple />
        </div>
        <div className="mb-3">
          <Label label={t('assigned_stage')} />
          <AsyncSelect onChange={(value: any) => handleFilterInputChange({ setFilter, key: 'opportunity_status_id', value: value, valueType: 'A' })} loadOptions={fetchAllOpportunityStages} multiple />
        </div>
      </FilterPopup>
    </>
  );
}

export default TaskConfigFilter;
