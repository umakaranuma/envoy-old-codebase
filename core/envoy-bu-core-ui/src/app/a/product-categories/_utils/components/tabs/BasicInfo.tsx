'use client';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { IOpportunityType } from '../../model';
import { useState } from 'react';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useParams } from 'next/navigation';
import { ProductCategoriesEdit } from '../ProductCategoriesEdit';

export const BasicInfo = ({ data, skeleton, onReload }: { data: IOpportunityType; skeleton: boolean; onReload: () => void }) => {
  const t = useTrans('label.product_categories,otr.common');
  const params = useParams();
  const categoryId = params.categoryId?.toString() || '';
  const [currentEditId, setCurrentEditId] = useState('');
  const handleAfterUpdate = () => {
    setCurrentEditId('');
    onReload();
  };
  return (
    <div className="p-2 bg-white px-4 rounded-2 rounded-top-0">
      <div className="row">
        <div className="col-12 col-md-6 mb-3">
          <Description label={t('title')} value={data?.title || '-'} skeleton={skeleton} />
        </div>
        <div className="col-12 col-md-6 mb-3">
          <Description label={t('description')} value={data?.description || '-'} skeleton={skeleton} />
        </div>
      </div>
      <div className="d-flex justify-content-end gap-2">
        <Button onClick={() => setCurrentEditId(categoryId)}>
          <span className="d-flex gap-2">
            <Flexicon icon="pencil-line" variant="line" size={17} />
            <span>{t('edit')}</span>
          </span>
        </Button>
      </div>
      {currentEditId !== '' && <ProductCategoriesEdit editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />}
    </div>
  );
};
