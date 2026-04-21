import { useEffect, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import { getAllPermissions, getAllRolePermissions, getOneRoles } from '../api-service';
import { EntityItem, IRoles, ModuleItem, Permission } from '../model';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { Accordion, AccordionItem } from '@apptimus-ui/accordion';

export const RolesView = ({ isOpen, viewId, onClose, setEditId }: { isOpen: boolean; viewId: string; onClose: Function; setEditId: Function }) => {
  const t = useTrans('label.role,otr.common');
  const [data, setData] = useState({} as IRoles);
  const [skeleton, setSkeleton] = useState(true);
  const [permissiondata, setPermissionData] = useState<{ result: ModuleItem[] }>({ result: [] });
  const [selectedPermissions, setSelectedPermissions] = useState<number[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneRoles(viewId);
      responseData?.is_success && (setData(responseData.result), setSkeleton(false));

      const responsePermissions = await getAllPermissions('CORE,CRM');
      if (responsePermissions?.is_success) {
        setPermissionData({ result: responsePermissions.result || [] });
      }

      const permissions = await getAllRolePermissions(viewId);
      if (permissions?.is_success && Array.isArray(permissions.result.permissions)) {
        const permissionIds = permissions.result.permissions;
        setSelectedPermissions(permissionIds);
      } else {
        setSelectedPermissions([]);
      }
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  const handleEdit = () => {
    onClose();
    setTimeout(() => {
      setEditId(viewId);
    }, 100);
  };

  return (
    <Modal isOpen={isOpen} size="lg">
      <ModalHeader title={t('user_roles')} onClose={() => onClose()} />
      <ModalBody>
        <div className="row">
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('user_role_name')} value={data?.name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('description')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
          <div className="role-accordion">
            <Accordion>
              {permissiondata.result.map((moduleItem: ModuleItem, moduleIndex: number) => (
                <AccordionItem
                  key={moduleIndex}
                  title={moduleItem.module}
                  startContent={
                    <input
                      disabled
                      type="checkbox"
                      className="form-check-input"
                      checked={moduleItem.permissions.every((p) => selectedPermissions?.includes(p.id))}
                      onClick={(e) => e.stopPropagation()}
                      defaultChecked={moduleItem.permissions.every((p) => selectedPermissions?.includes(p.id))}
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
                              disabled
                              type="checkbox"
                              className="form-check-input m-0"
                              checked={entityItem.actions.every((p) => selectedPermissions.includes(p.id))}
                              defaultChecked={entityItem.actions.every((p) => selectedPermissions.includes(p.id))}
                            />
                            <span className="fs-base text-muted">{entityItem.entity}</span>
                          </label>
                          <div className="d-flex flex-column">
                            {entityItem.actions.map((action: Permission, actionIndex: number) => (
                              <div className="form-check d-flex align-items-center gap-2 ps-3 fs-base" key={actionIndex}>
                                <input
                                  disabled
                                  className="form-check-input pointer m-0"
                                  id={`${entityItem.entity}-${action.id}`}
                                  type="checkbox"
                                  checked={selectedPermissions.includes(action.id)}
                                  defaultChecked={selectedPermissions.includes(action.id)}
                                />
                                <label className="form-check-label pointer m-0" style={{ opacity: 'initial' }} htmlFor={`${entityItem.entity}-${action.id}`}>
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
          <Button text={t('edit')} type="submit" width="sm" onClick={handleEdit} />
          <Button text={t('close')} color="light" width="sm" onClick={() => onClose()} />
        </div>
      </ModalFooter>
    </Modal>
  );
};
