import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { AsyncSelect } from '@apptimus-ui/select';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import CreateField from '../CreateField';
import { fetchAllUsers } from '../../../service';

function Mapping() {
  const t = useTrans('label.invoice,otr.common,be.msg');
  const [createFormVisible, setCreateFormVisible] = useState(false);

  return (
    <div className="bg-white custom-card p-3 rounded-3 mb-3">
      <div className="fs-15 fw-semibold">{t('mapping_payment_from_external_file')}</div>
      {/* <div className="row col-6 border border-dark rounded-2">
                        <div className="col-6 p-2 text-center border-end border-dark font-medium fs-14"> {t('system_field_name')}</div>
                        <div className="col-6 p-2 text-center font-medium fs-14"> {t('excel_field_name')}</div>
                        <div>
                            <div className='col-6 text-center border-end border-dark'>
                                <Label label={'Invoice Number'} />
                            </div>
                            <div className='col-6 text-center'>
                                <Label label={'Invoice Number'} />
                            </div>
                        </div>
                    </div> */}
      <div className="d-flex justify-content-end align-items-center mb-3">
        <Button className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)} size="md" color="primary">
          <Flexicon icon="plus-circle" size={18} />
          <span className="d-none d-sm-inline">{t('add_new')}</span>
        </Button>
      </div>
      <div className="col-lg-6">
        <table className="table table-bordered align-middle">
          <thead className="table-light">
            <tr className="text-center">
              <th className="w-50">{t('system_field_name')}</th>
              <th className="w-50">{t('excel_field_name')}</th>
            </tr>
          </thead>
          <tbody>
            {fieldPairs.map((field, index) => (
              <tr key={index}>
                <td>
                  <Label label={field} isRequired />
                </td>
                <td>
                  <div className="custom-select">
                    <AsyncSelect
                      onChange={(value) => console.log('policy_id', value)}
                      className="form-control error-policy_id"
                      option={{ label: 'brokerage_policy_id', value: 'id' }}
                      isSearchable={true}
                      loadOptions={(searchValue: any, currentPage: any) => fetchAllUsers(searchValue, currentPage)}
                    />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {createFormVisible && <CreateField isOpen={createFormVisible} onCancel={() => setCreateFormVisible(false)} />}
    </div>
  );
}

export default Mapping;

const fieldPairs = ['Invoice Number', 'Invoice Date', 'Policy Info', 'Insurer Info', 'Settled Amount', 'Outstanding Amount'];
