import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { EntityItem, initFormData, IRoles, ModuleItem, Permission } from '../model';
import { getAllPermissions, getAllRolePermissions, getOneRoles, storeRolePermissions, updateRoles } from '../api-service';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { Accordion, AccordionItem } from '@apptimus-ui/accordion';

type Data = {
  result: ModuleItem[];
};

export const RolesEdit = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.role,otr.common');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [skeleton, setSkeleton] = useState(true);
  const [data, setData] = useState<Data>({ result: [] });
  const [selectedPermissions, setSelectedPermissions] = useState<number[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      setSkeleton(true);

      const responseData = await getOneRoles(editId);
      if (responseData?.is_success) {
        const data: IRoles = responseData.result;
        onFormChange('name', data.name);
        onFormChange('description', data.description);

        const responsePermissions = await getAllPermissions('CORE,CRM');
        if (responsePermissions?.is_success) {
          setData({ result: responsePermissions.result || [] });
        }

        const permissions = await getAllRolePermissions(editId);
        if (permissions?.is_success && Array.isArray(permissions.result.permissions)) {
          const permissionIds = permissions.result.permissions;
          setSelectedPermissions(permissionIds);
        } else {
          setSelectedPermissions([]);
        }
      }
      setSkeleton(false);
    };

    if (editId) {
      fetchData();
    }
  }, [editId]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  const tBe = useTrans('be.msg,be.error,be.attri');
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.roles_crud.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateRoles(editId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.roles_crud.update, tBe);
      }

      if (responseData.is_success) {
        if (selectedPermissions.length === 0) {
          toaster.success(tBe(responseData.message));
          return;
        }

        const responsePerm = await storeRolePermissions(responseData.result.id, { permissions: selectedPermissions });
        if (responsePerm.is_success) {
          toaster.success(tBe(responseData.message));
        }
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
      <ModalHeader title={t('edit_user_role')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.roles_crud.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="name" label={t('user_role_name')} isRequired />
              {skeleton ? <InputSkeleton /> : <Input value={formData.name || ''} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" id="name" name="name" />}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="description" label={t('description')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.description || ''}
                  onChange={(e) => onFormChange('description', e.target.value)}
                  className="form-control error-description"
                  id="description"
                  name="description"
                />
              )}
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
                        checked={moduleItem.permissions.every((p) => selectedPermissions?.includes(p.id))}
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
            <Button text={t('update')} type="submit" width="sm" isLoading={isFormProcessing} disabled={skeleton} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
};
