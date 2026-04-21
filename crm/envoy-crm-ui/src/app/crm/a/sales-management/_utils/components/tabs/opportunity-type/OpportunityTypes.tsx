import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import AddType from './AddType';
import { useParams } from 'next/navigation';
import { IType } from '../../../model';
import { deleteOpportunityType, getAllTypesOfOpportunity } from '../../../api-service';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { toaster } from '@/helpers/services/toaster';
import RiskTypes from './risk-type/RiskTypes';
import BulkUpload from './risk-type/BulkUpload';

const OpportunityTypes = ({ customerId }: { customerId?: number | null }) => {
  const t = useTrans('label.sales_managements,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const params = useParams();
  const opportunityId = params.managementId?.toString() || '';
  const [isOpen, setIsOpen] = useState(false);
  const [selectedTypeId, setSelectedTypeId] = useState('');
  const [data, setData] = useState<IType[]>([]);
  const [skeleton, setSkeleton] = useState(true);
  const [isBulkUploadOpen, setIsBulkUploadOpen] = useState(false);

  useEffect(() => {
    if (opportunityId) {
      fetchData();
    }
  }, [opportunityId]);

  const fetchData = async () => {
    setSkeleton(true);
    try {
      const responseData = await getAllTypesOfOpportunity(opportunityId);
      if (responseData?.is_success) {
        setData(responseData.result);
        if (responseData.result.length > 0) {
          if (!responseData.result.some((item: any) => item.id === selectedTypeId)) {
            setSelectedTypeId(responseData.result[0].id);
          }
        } else {
          setSelectedTypeId('');
        }
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setSkeleton(false);
    }
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function) => {
    setLoader(true);
    try {
      const responseData = await deleteOpportunityType(opportunityId, deleteId);
      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        callback();
        await fetchData();
        if (selectedTypeId === deleteId) {
          setSelectedTypeId('');
        }
      }
    } finally {
      setLoader(false);
    }
  };

  const handleTypeSelect = (typeId: string) => {
    setSelectedTypeId(typeId);
  };

  return (
    <>
      <div className="row  ">
        <div>
          {skeleton ? (
            <div className="d-flex gap-3">
              <Skeleton width="100px" height="26px" className="mt-1" />
              <Skeleton width="100px" height="26px" className="mt-1" />
              <Skeleton width="100px" height="26px" className="mt-1" />
            </div>
          ) : (
            <div className="d-flex justify-content-between">
              <div className="d-flex algin-items-center pointer gap-2">
                {data.map((type: IType) => (
                  <div className="d-flex flex-row" key={`type-${type.id}`}>
                    <div onClick={() => handleTypeSelect(type.id)} className={`risk-type-badge ${selectedTypeId === type.id ? 'bg-primary text-white' : 'bg-light'}`}>
                      <span>{type.title}</span>
                    </div>
                    <div onClick={(e: React.MouseEvent) => e.stopPropagation()} className="risk-type-badge-delete bg-light">
                      <DeleteConfirmPop trigger={<Flexicon icon="x-close" variant="line" size={15} className="text-danger" />} deleteId={type.id} handleOnDelete={handleOnDelete} />
                    </div>
                  </div>
                ))}
                <div onClick={() => setIsOpen(true)} role="button" className="risk-type-badge risk-type-badge-add bg-primary">
                  <Flexicon icon="plus" variant="line" size={15} className="rounded-full" />
                  <span className="pe-1 fs-12">{t('add')}</span>
                </div>
              </div>
              <div>
                <Button
                  color="light"
                  className="d-flex align-items-center gap-1"
                  size="sm"
                  onClick={() => {
                    setIsBulkUploadOpen(true);
                  }}
                >
                  <Flexicon icon="upload-01" variant="line" size={18} />
                  <span className="d-none d-sm-inline">{t('upload_info')}</span>
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {selectedTypeId && <RiskTypes selectedTypeId={selectedTypeId} leadId={opportunityId} customerId={customerId?.toString() || ''} key={`risk-types-${selectedTypeId}`} />}

      {isOpen && <AddType isOpen={isOpen} onCancel={() => setIsOpen(false)} afterSave={fetchData} />}
      {isBulkUploadOpen && (
        <BulkUpload
          isOpen={isBulkUploadOpen}
          onCancel={() => setIsBulkUploadOpen(false)}
          afterSave={() => {
            setIsBulkUploadOpen(false);
          }}
          riskTypeIds={data.map((item) => item.id)}
          leadId={opportunityId}
        />
      )}
    </>
  );
};

export default OpportunityTypes;
