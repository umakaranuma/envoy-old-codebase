import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { IFlags, initFormData } from '../model';
import { getOneFlags, updateFlags } from '../api-service';
import { Select } from '@apptimus-ui/select';
import TeamList from './TeamList';

export const MappingDataTablePreviewEdit = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.mapping_data_table_preview,otr.common');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [skeleton, setSkeleton] = useState(false);
  const [transactionType, setTransactionType] = useState('brokerage');
  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneFlags(editId);

      if (responseData?.is_success) {
        const data: IFlags = responseData.result;
        onFormChange('name', data.name);
        onFormChange('description', data.description);
        onFormChange('color', data.color);
        setSkeleton(false);
      }
    };

    if (editId) {
      setSkeleton(true);
      fetchData();
    }
  }, [editId]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  const tBe = useTrans('be.msg,be.error,be.attri');
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.flag_crud.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateFlags(editId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.flag_crud.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(initFormData);
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }
  const people = [
    {
      id: 1,
      firstName: 'Olivia Rhye',
      lastName: 'Medhurst',
      type: 'account-manager',
    },
    {
      id: 2,
      firstName: 'Michael Scott',
      lastName: 'Scott',
      type: 'sales-team',
    },
    {
      id: 3,
      firstName: 'Jim Halpert',
      lastName: 'Beesly',
      type: 'sales-team',
    },
    {
      id: 4,
      firstName: 'Olivia Rhye2',
      lastName: 'Medhurst',
      type: 'account-manager',
    },
    {
      id: 5,
      firstName: 'Michael Scott',
      lastName: 'Scott',
      type: 'account-manager',
    },
  ];
  const [viewSalesTeam, setViewSalesTeam] = useState(false);
  const [accountManagers, setAccountManagers] = useState(people.filter((p) => p.type === 'account-manager').map((p) => ({ id: String(p.id), name: p.firstName })));
  const [teamMembers, setTeamMembers] = useState(people.filter((p) => p.type === 'sales-team').map((p) => ({ id: String(p.id), name: p.firstName })));
  const handleRemove = (id: string, isManager: boolean) => {
    if (isManager) {
      setAccountManagers((prev) => prev.filter((user) => String(user.id) !== id));
    } else {
      setTeamMembers((prev) => prev.filter((user) => String(user.id) !== id));
    }
  };
  return (
    <Modal isOpen={isOpen} size={'lg'}>
      <ModalHeader title={t('edit_mapping_details')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.flag_crud.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <div className="col-12 col-md-6">
                <Label htmlFor="product_name" label={t('product_name')} isRequired />
                <Select
                  onChange={(value) => {
                    console.log('value: ', value);
                  }}
                  options={[
                    {
                      id: 1,
                      firstName: 'Product A',
                      lastName: 'Medhurst',
                    },
                    {
                      id: 2,
                      firstName: 'Product B',
                      lastName: 'Medhurst',
                    },
                  ]}
                  option={{
                    label: 'firstName',
                    value: 'id',
                    keysToSearch: ['firstName', 'lastName', 'id'],
                  }}
                />
              </div>
              <div className="col-12 col-md-6 mt-2">
                <Label htmlFor="insurer_info" label={t('insurer_info')} isRequired />
                <Select
                  onChange={(value) => {
                    console.log('value: ', value);
                  }}
                  options={[
                    {
                      id: 1,
                      firstName: 'Ceylinco General Insurance',
                      lastName: 'Medhurst',
                    },
                    {
                      id: 2,
                      firstName: 'Ceylinco General Insurance 2',
                      lastName: 'Medhurst',
                    },
                  ]}
                  option={{
                    label: 'firstName',
                    value: 'id',
                    keysToSearch: ['firstName', 'lastName', 'id'],
                  }}
                />
              </div>
              <div className="col-12 col-md-12 mt-2">
                <Label htmlFor="New Business" label="New Business" isRequired />
                <div className="d-flex gap-2">
                  <div className="form-check">
                    <Input
                      type="radio"
                      id="New Business"
                      name="commission-type"
                      className="form-check-input pointer"
                      checked={transactionType === 'New Business'}
                      onChange={() => setTransactionType('New Business')}
                    />
                    <label className="form-check-label" htmlFor="New Business">
                      New Business
                    </label>
                  </div>
                  <div className="form-check">
                    <Input
                      type="radio"
                      id="Renewal"
                      name="commission-type"
                      className="form-check-input pointer"
                      checked={transactionType === 'Renewal'}
                      onChange={() => setTransactionType('Renewal')}
                    />
                    <label className="form-check-label" htmlFor="Renewal">
                      Renewal
                    </label>
                  </div>
                  <div className="form-check">
                    <Input
                      type="radio"
                      id="Additions"
                      name="commission-type"
                      className="form-check-input pointer"
                      checked={transactionType === 'Additions'}
                      onChange={() => setTransactionType('Additions')}
                    />
                    <label className="form-check-label" htmlFor="Additions">
                      Additions
                    </label>
                  </div>
                </div>
              </div>
            </div>
            {/* sales team */}
            <div className="col-12 col-md-12 mt-2">
              <Label htmlFor="sales_team" label={t('sales_team')} isRequired />
              <Select
                options={[
                  {
                    id: 1,
                    firstName: 'Team A',
                    lastName: 'Medhurst',
                  },
                  {
                    id: 2,
                    firstName: 'Team B',
                    lastName: 'Medhurst',
                  },
                ]}
                option={{
                  label: 'firstName',
                  value: 'id',
                  // renderOption: () => <><TeamList onRemove={handleRemove} accountManagers={accountManagers} teamMembers={teamMembers} /></>,
                  keysToSearch: ['firstName'],
                }}
                onChange={(_value, selectedData) => {
                  setViewSalesTeam(true);
                  console.log('selectedData', selectedData);
                }}
              />
              {viewSalesTeam && <TeamList onRemove={handleRemove} accountManagers={accountManagers} teamMembers={teamMembers} />}
            </div>
            {/* separate */}
            <div className="d-flex">
              <div className="col-12 col-md-6 mt-2">
                <Label htmlFor="commission_type" label={t('commission_type')} isRequired />
                <div className="d-flex gap-2">
                  <div className="form-check">
                    <Input
                      type="radio"
                      id="commission_type"
                      name="commission-type"
                      className="form-check-input pointer"
                      checked={transactionType === 'commission_type'}
                      onChange={() => setTransactionType('commission_type')}
                    />
                    <label className="form-check-label" htmlFor="commission_type">
                      {t('fixed')}
                    </label>
                  </div>
                  <div className="form-check">
                    <Input
                      type="radio"
                      id="Renewal"
                      name="commission-type"
                      className="form-check-input pointer"
                      checked={transactionType === 'Renewal'}
                      onChange={() => setTransactionType('Renewal')}
                    />
                    <label className="form-check-label" htmlFor="Renewal">
                      {t('percentage')}
                    </label>
                  </div>
                </div>
              </div>
              <div>
                <Input
                  label={t('commission_percentage')}
                  value={formData.description}
                  onChange={(e) => onFormChange('description', e.target.value)}
                  className="form-control error-description"
                  name="description"
                />
              </div>
            </div>
            {/*  */}
            <div className="d-flex">
              <div className="col-12 col-md-6">
                <Label htmlFor="commission_type" label={t('commission_type')} isRequired />
                <div className="d-flex gap-2">
                  <div className="form-check">
                    <Input
                      type="radio"
                      id="commission_type"
                      name="commission-type"
                      className="form-check-input pointer"
                      checked={transactionType === 'commission_type'}
                      onChange={() => setTransactionType('commission_type')}
                    />
                    <label className="form-check-label" htmlFor="commission_type">
                      {t('fixed')}
                    </label>
                  </div>
                  <div className="form-check">
                    <Input
                      type="radio"
                      id="Renewal"
                      name="commission-type"
                      className="form-check-input pointer"
                      checked={transactionType === 'Renewal'}
                      onChange={() => setTransactionType('Renewal')}
                    />
                    <label className="form-check-label" htmlFor="Renewal">
                      {t('percentage')}
                    </label>
                  </div>
                </div>
              </div>
              <div>
                <Input
                  label={t('revised_commission_percentage')}
                  value={formData.description}
                  onChange={(e) => onFormChange('description', e.target.value)}
                  className="form-control error-description"
                  name="description"
                />
              </div>
            </div>
            {/*  */}
            <div className="d-flex">
              <div className="col-12 col-md-6">
                <Label htmlFor="commission_type" label={t('commission_type')} isRequired />
                <div className="d-flex gap-2">
                  <div className="form-check">
                    <Input
                      type="radio"
                      id="commission_type"
                      name="commission-type"
                      className="form-check-input pointer"
                      checked={transactionType === 'commission_type'}
                      onChange={() => setTransactionType('commission_type')}
                    />
                    <label className="form-check-label" htmlFor="commission_type">
                      {t('fixed')}
                    </label>
                  </div>
                  <div className="form-check">
                    <Input
                      type="radio"
                      id="Renewal"
                      name="commission-type"
                      className="form-check-input pointer"
                      checked={transactionType === 'Renewal'}
                      onChange={() => setTransactionType('Renewal')}
                    />
                    <label className="form-check-label" htmlFor="Renewal">
                      {t('percentage')}
                    </label>
                  </div>
                </div>
              </div>
              <div>
                <Input
                  label={t('bonus_commission_percentage')}
                  value={formData.description}
                  onChange={(e) => onFormChange('description', e.target.value)}
                  className="form-control error-description"
                  name="description"
                />
              </div>
            </div>
            {/*  */}
            <div className="d-flex">
              <div className="col-12 col-md-6">
                <Label htmlFor="commission_type" label={t('commission_type')} isRequired />
                <div className="d-flex gap-2">
                  <div className="form-check">
                    <Input
                      type="radio"
                      id="commission_type"
                      name="commission-type"
                      className="form-check-input pointer"
                      checked={transactionType === 'commission_type'}
                      onChange={() => setTransactionType('commission_type')}
                    />
                    <label className="form-check-label" htmlFor="commission_type">
                      {t('fixed')}
                    </label>
                  </div>
                  <div className="form-check">
                    <Input
                      type="radio"
                      id="Renewal"
                      name="commission-type"
                      className="form-check-input pointer"
                      checked={transactionType === 'Renewal'}
                      onChange={() => setTransactionType('Renewal')}
                    />
                    <label className="form-check-label" htmlFor="Renewal">
                      {t('percentage')}
                    </label>
                  </div>
                </div>
              </div>
              <div>
                <Input
                  label={t('target_achievements_commission_percentage')}
                  value={formData.description}
                  onChange={(e) => onFormChange('description', e.target.value)}
                  className="form-control error-description"
                  name="description"
                />
              </div>
            </div>
            {/*  */}
            <div className="d-flex">
              <div className="col-12 col-md-6">
                <Label htmlFor="created_by" label={t('created_by')} isRequired />
                <div className="mx-2">
                  <Select
                    onChange={(value) => {
                      console.log('value: ', value);
                    }}
                    options={[
                      {
                        id: 1,
                        firstName: 'xyz',
                        lastName: 'Medhurst',
                      },
                      {
                        id: 2,
                        firstName: 'abc',
                        lastName: 'Medhurst',
                      },
                    ]}
                    option={{
                      label: 'firstName',
                      value: 'id',
                      keysToSearch: ['firstName', 'lastName', 'id'],
                    }}
                  />
                </div>
              </div>
              <div>
                <Input
                  label={t('date')}
                  value={formData.description}
                  onChange={(e) => onFormChange('description', e.target.value)}
                  className="form-control error-description"
                  name="description"
                  type="date"
                />
              </div>
            </div>
            {/*  */}
            <div className="d-flex">
              <div className="col-12 col-md-6">
                <Label htmlFor="updated_by" label={t('updated_by')} isRequired />
                <div className="mx-2">
                  <Select
                    onChange={(value) => {
                      console.log('value: ', value);
                    }}
                    options={[
                      {
                        id: 1,
                        firstName: 'xyz',
                        lastName: 'Medhurst',
                      },
                      {
                        id: 2,
                        firstName: 'abc',
                        lastName: 'Medhurst',
                      },
                    ]}
                    option={{
                      label: 'firstName',
                      value: 'id',
                      keysToSearch: ['firstName', 'lastName', 'id'],
                    }}
                  />
                </div>
              </div>
              <div>
                <Input
                  label={t('date')}
                  value={formData.description}
                  onChange={(e) => onFormChange('description', e.target.value)}
                  className="form-control error-description"
                  name="description"
                  type="date"
                />
              </div>
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('update')} type="submit" width="sm" isLoading={isFormProcessing} disabled={skeleton} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
};
