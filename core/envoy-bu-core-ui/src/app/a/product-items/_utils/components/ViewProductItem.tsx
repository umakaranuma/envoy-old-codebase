'use client';
import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { getOneProductItem } from '../api-service';
import { Description } from '@/components/others/Description';

export function ViewProductItem({ isOpen, onCancel, viewId }: { isOpen: boolean; onCancel: Function; viewId: string }) {
  const t = useTrans('label.product_item,otr.common');
  const [formData, setFormData] = useState({ title: '', description: '' });
  const [skeleton, setSkeleton] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneProductItem(viewId);
      if (responseData?.is_success) {
        setFormData(responseData.result);
      }

      setSkeleton(false);
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  return (
    <Modal isOpen={isOpen} scrollable>
      <ModalHeader title={t('product_item')} onClose={() => onCancel()} />
      <ModalBody>
        <div id={`${form.product_item.update}`} className="row">
          <div className="col-12 mb-4">
            <Description label={t('title')} value={formData.title} skeleton={skeleton} />
          </div>
          <div className="col-12 mb-2">
            <Description label={t('description')} value={formData.description} skeleton={skeleton} />
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('close')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}
