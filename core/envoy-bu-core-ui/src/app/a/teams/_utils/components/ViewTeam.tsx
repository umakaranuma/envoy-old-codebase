'use client';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Badge, Button, Label, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITeam } from '../model';
import { getOneTeam } from '../api-service';
import { Description } from '@/components/others/Description';
import S3Avatar from '@/components/others/page-related/S3Avatar';

export function ViewTeam({ isOpen, onCancel, viewId, handleOpenEdit }: { isOpen: boolean; onCancel: Function; viewId: string; handleOpenEdit: Function }) {
  const t = useTrans('label.teams,otr.common');
  const [data, setData] = useState({} as ITeam);
  const [skeleton, setSkeleton] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneTeam(viewId);
      if (responseData?.is_success) {
        const data = responseData.result;
        setData(data);
        setSkeleton(false);
      }
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  return (
    <Modal isOpen={isOpen} size="lg">
      <ModalHeader title={t('team')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row">
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('team_name')} value={data?.name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('team_lead')} value={data?.manager_name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('description')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 mb-3">
            <Label label={t('products')} />
            {skeleton ? (
              <Skeleton width="100%" height="100px" />
            ) : (
              <div className="d-flex flex-row flex-wrap gap-2">
                {data.products?.map((product, key) => (
                  <div className="d-flex flex-row justify-content-between align-items-center border p-2 rounded-2 gap-5 bg-light" key={key}>
                    <div className="fw-medium">{product?.name}</div>
                    <div className="fs-12">
                      {t('code')}: {product.code}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="col-12 mb-3">
            <Label label={t('team_members')} />
            {skeleton ? (
              <Skeleton width="100%" height="100px" />
            ) : (
              <div className="d-flex flex-row flex-wrap gap-2">
                {data.sales_agents?.map((agent, key) => (
                  <div className="d-flex flex-row align-items-center gap-1 bg-light rounded-2 p-2 gap-4" key={key}>
                    <div className="d-flex flex-row align-items-center gap-1">
                      <div>
                        <S3Avatar imageKey={agent?.picture ? agent.picture : undefined} width={30} height={30} />
                      </div>
                      <div className="d-flex flex-column">
                        <div className="fw-medium fs-12">{agent?.display_name}</div>
                        <div className="fs-12">{agent?.email}</div>
                      </div>
                    </div>
                    <div>
                      <Badge variant="outline" text={agent.role_name} radius="pill" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('edit')} onClick={() => handleOpenEdit(viewId)} width="sm" isLoading={skeleton} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}
