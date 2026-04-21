import FilterPopup from '@/components/others/FilterPopup';
import { handleFilterInputChange } from '@/helpers/services/commonService';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect, Select } from '@apptimus-ui/select';
import { Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { opportunityTypes } from '../constants';
import { fetchAllCustomers } from '../services';
import S3Avatar from '@/components/others/page-related/S3Avatar';

type FilterProps = {
  isOpen: boolean;
  onSubmit: Function;
  onClose: Function;
};

function SalesManagementsFilter({ isOpen, onSubmit, onClose }: FilterProps) {
  const t = useTrans('label.sales_managements');
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
          <Label label={t('type')} />
          <Select
            onChange={(value) => handleFilterInputChange({ setFilter, key: 'type', value: value, valueType: 'A' })}
            option={{ label: 'label', value: 'value' }}
            isSearchable={false}
            options={opportunityTypes}
            multiple
          />
        </div>
        <div className="mb-3">
          <Label label={t('account')} />
          <AsyncSelect
            onChange={(value) => handleFilterInputChange({ setFilter, key: 'customer_id', value: value, valueType: 'A' })}
            option={{
              labelFn: (option) => (
                <>
                  <div className="text d-flex">
                    <S3Avatar imageKey={option.logo} width={35} height={35} />
                    <div>
                      <div>{option.name}</div>
                      <div className="text-muted fs-13">{option.code}</div>
                    </div>
                  </div>
                </>
              ),
              label: 'label',
              value: 'id',
            }}
            loadOptions={fetchAllCustomers}
            multiple
          />
        </div>
        {/* <div className="mb-3">
          <Label label={t('channel')} />
          <AsyncSelect
            onChange={(value) => handleFilterInputChange({ setFilter, key: 'channel_id', value: value, valueType: 'A' })}
            option={{
              label: 'name',
              value: 'id',
            }}
            loadOptions={fetchAllChannel}
            multiple
          />
        </div>
        <div className="mb-3">
          <Label label={t('progress_stage')} />
          <AsyncSelect onChange={(value: any) => handleFilterInputChange({ setFilter, key: 'stage_id', value: value, valueType: 'A' })} loadOptions={fetchAllOpportunityStages} multiple />
        </div>
        <div className="mb-3">
          <Label label={t('currency')} />
          <AsyncSelect
            onChange={(value: any) => handleFilterInputChange({ setFilter, key: 'currency_id', value: value, valueType: 'A' })}
            loadOptions={fetchAllCurrency}
            option={{ label: 'symbol', value: 'id' }}
            multiple
          />
        </div>
        <div className="mb-3">
          <Label label={t('health')} />
          <Select
            onChange={(value: any) => handleFilterInputChange({ setFilter, key: 'health', value: value })}
            option={{ label: 'label', value: 'value' }}
            isSearchable={false}
            options={healthCount}
          />
        </div> */}
      </FilterPopup>
    </>
  );
}

export default SalesManagementsFilter;
