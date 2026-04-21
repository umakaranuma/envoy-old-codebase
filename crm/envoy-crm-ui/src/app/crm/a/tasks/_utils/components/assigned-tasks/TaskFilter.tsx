import FilterPopup from '@/components/others/FilterPopup';
import { handleFilterInputChange, hexToRgba } from '@/helpers/services/commonService';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect } from '@apptimus-ui/select';
import { Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { fetchAllAssigneesDropdownData, fetchAllTaskStatuses } from '../../service';
import { fetchAllOpportunities, fetchAllOpportunityStages } from '@/app/crm/a/sales-management/_utils/services';
import S3Avatar from '@/components/others/page-related/S3Avatar';

type FilterProps = {
  isOpen: boolean;
  onSubmit: Function;
  onClose: Function;
  opId?: string;
};

function TaskFilter({ isOpen, onSubmit, onClose, opId }: FilterProps) {
  const t = useTrans('label.tasks');
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
          <Label label={t('assigned_to')} />
          <AsyncSelect
            onChange={(value: any) => {
              console.log('value', value);
              handleFilterInputChange({ setFilter, key: 'assigned_to_id', value: value, valueType: 'A' });
            }}
            loadOptions={fetchAllAssigneesDropdownData}
            option={{
              labelFn: (option) => (
                <>
                  <div className="text d-flex">
                    <S3Avatar imageKey={option.picture} width={35} height={35} />
                    <div>
                      <div>{option.display_name}</div>
                      <div className="text-muted">{option.email}</div>
                    </div>
                  </div>
                </>
              ),
              label: 'display_name',
              value: 'id',
            }}
            multiple
          />
        </div>
        {opId === '' && (
          <>
            <div className="mb-3">
              <Label label={t('lead')} />
              <AsyncSelect
                onChange={(value: any) => handleFilterInputChange({ setFilter, key: 'opportunity_id', value: value, valueType: 'A' })}
                loadOptions={(searchValue: any, currentPage: any) => fetchAllOpportunities(searchValue, currentPage)}
                option={{
                  labelFn: (option) => (
                    <>
                      <div className="text">{option.title}</div>
                      <div className="d-flex align-items-center gap-2 mt-1">
                        <div
                          className={`rounded-5 fw-semibold badge`}
                          style={{ background: hexToRgba(option.stage_color, 0.1), border: `1px solid ${hexToRgba(option.stage_color, 0.4)}`, color: option.stage_color }}
                        >
                          {option.stage_name}
                        </div>
                        <div className="text-muted">|</div>
                        <div className="text">{option.code}</div>
                      </div>
                    </>
                  ),
                  label: 'title',
                  value: 'id',
                }}
                multiple
              />
            </div>
            <div className="mb-3">
              <Label label={t('lead_stage')} />
              <AsyncSelect
                onChange={(value: any) => handleFilterInputChange({ setFilter, key: 'opportunity_status_id', value: value, valueType: 'A' })}
                loadOptions={fetchAllOpportunityStages}
                multiple
              />
            </div>
          </>
        )}
        <div className="mb-3">
          <Label label={t('task_status')} />
          <AsyncSelect onChange={(value: any) => handleFilterInputChange({ setFilter, key: 'task_status_id', value: value, valueType: 'A' })} loadOptions={fetchAllTaskStatuses} multiple />
        </div>
      </FilterPopup>
    </>
  );
}

export default TaskFilter;
