import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { EntityItem, initFormData, ModuleItem, Permission } from '../model';
import { toaster } from '@/helpers/services/toaster';
import { createRoles, getAllPermissions, storeRolePermissions } from '../api-service';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { Accordion, AccordionItem } from '@apptimus-ui/accordion';

type Data = {
  result: ModuleItem[];
};

function RolesCreate({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.role,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [data, setData] = useState<Data>({ result: [] });
  const [selectedPermissions, setSelectedPermissions] = useState<number[]>([]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
    clearError(form.roles_crud.store, name);
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.roles_crud.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createRoles(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.roles_crud.store, tBe);
      }

      if (responseData.is_success) {
        if (selectedPermissions.length === 0) {
          afterSave();
          toaster.success(tBe(responseData.message));
          return;
        }

        const responsePerm = await storeRolePermissions(responseData.result.id, { permissions: selectedPermissions });
        if (responsePerm.is_success) {
          afterSave();
          toaster.success(tBe(responseData.message));
        }
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  useEffect(() => {
    const fetchData = async () => {
      try {
        const responseData = await getAllPermissions('CORE,CRM');

        if (responseData?.is_success) {
          setData({ result: responseData.result || [] });
        }
      } catch (error) {
        console.error('Error fetching permissions:', error);
      }
    };

    fetchData();
  }, []);

  const togglePermission = (id: number) => {
    setSelectedPermissions((prev) => (prev.includes(id) ? prev.filter((permId) => permId !== id) : [...prev, id]));
  };

  const toggleEntity = (_entity: string, permissions: Permission[]) => {
    const allSelected = permissions.every((p) => selectedPermissions.includes(p.id));
    setSelectedPermissions((prev) => (allSelected ? prev.filter((id) => !permissions.some((p) => p.id === id)) : [...new Set([...prev, ...permissions.map((p) => p.id)])]));
  };

  const toggleModule = (_module: string, permissions: Permission[]) => {
    const allSelected = permissions.every((p) => selectedPermissions.includes(p.id));
    setSelectedPermissions((prev) => (allSelected ? prev.filter((id) => !permissions.some((p) => p.id === id)) : [...new Set([...prev, ...permissions.map((p) => p.id)])]));
  };

  return (
    <Modal isOpen={isOpen} size="lg">
      <ModalHeader title={t('add_new_user_role')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.roles_crud.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('user_role_name')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                label={t('description')}
                value={formData.description}
                onChange={(e) => onFormChange('description', e.target.value)}
                className="form-control error-description"
                name="description"
              />
            </div>
            <div className="role-accordion">
              <Accordion>
                {data.result.map((moduleItem: ModuleItem, moduleIndex: number) => (
                  <AccordionItem
                    key={moduleIndex}
                    title={moduleItem.module}
                    startContent={
                      <input
                        type="checkbox"
                        className="form-check-input pointer"
                        checked={moduleItem.permissions.every((p) => selectedPermissions.includes(p.id))}
                        onChange={() => toggleModule(moduleItem.module, moduleItem.permissions)}
                        onClick={(e) => e.stopPropagation()}
                      />
                    }
                  >
                    <div className="row Accordio-item-permission-padding-add">
                      {moduleItem.permissions
                        .reduce<EntityItem[]>((acc: EntityItem[], permission: Permission) => {
                          const entityIndex = acc.findIndex((item: EntityItem) => item.entity === permission.entity);
                          if (entityIndex !== -1) {
                            acc[entityIndex].actions.push(permission);
                          } else {
                            acc.push({ entity: permission.entity, actions: [permission] });
                          }
                          return acc;
                        }, [])
                        .map((entityItem: EntityItem, entityIndex: number) => (
                          <div key={entityIndex} className="col-md-4 mb-4">
                            <label className="d-flex align-items-center gap-2 pointer mb-2">
                              <input
                                type="checkbox"
                                className="form-check-input pointer m-0"
                                checked={entityItem.actions.every((p) => selectedPermissions.includes(p.id))}
                                onChange={() => toggleEntity(entityItem.entity, entityItem.actions)}
                              />
                              <span className="fs-base text-muted">{entityItem.entity}</span>
                            </label>
                            <div className="d-flex flex-column">
                              {entityItem.actions.map((action: Permission, actionIndex: number) => (
                                <div className="form-check d-flex align-items-center gap-2 ps-3 fs-base" key={actionIndex}>
                                  <input
                                    className="form-check-input pointer m-0"
                                    id={`${entityItem.entity}-${action.id}`}
                                    type="checkbox"
                                    checked={selectedPermissions.includes(action.id)}
                                    onChange={() => togglePermission(action.id)}
                                  />
                                  <label className="form-check-label pointer m-0" htmlFor={`${entityItem.entity}-${action.id}`}>
                                    {action.action.replace('_', ' ')}
                                  </label>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                    </div>
                  </AccordionItem>
                ))}
              </Accordion>
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('create')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default RolesCreate;
