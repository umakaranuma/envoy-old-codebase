import sendRequest from 'apptimus-netlink';
import { useEffect, useState } from 'react';
import { InputSkeleton } from './InputSkeleton';
import { responseHandling } from '@/helpers/handlers/responseHandler';
import { Input, Label } from '@apptimus-ui/ui-element';
import { useTrans } from '@/helpers/services/lang/langService';

export interface IEntity {
  id: string;
  flex_field_values: { [key: string]: string };
  created_at: string;
  created_by_name: string;
  created_by_profile: string;
  updated_by_name: string;
  updated_by_profile: string;
}

export interface IFlexField {
  id: string;
  entity_type: string;
  field_code: string;
  field_label: string;
  data_type: string;
  default_value: string;
  is_mandatory: number;
  is_enabled: number;
  is_fixed: number;
  deleted_at: string | null;
}

export const emptyFlexField = {
  id: '',
  entity_type: '',
  field_code: '',
  field_label: '',
  data_type: '',
  default_value: '',
  is_mandatory: '',
  is_enabled: '1',
  is_fixed: '',
};

export const useFlexField = (entity: any) => {
  const [fields, setFields] = useState([] as IFlexField[]);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOne(entity);

      responseData?.is_success && setFields(responseData.result);
    };

    fetchData();
  }, []);

  return { fields };
};

const renderFieldElement = (field: IFlexField, value: any, onChange: Function, skeleton: boolean) => {
  const t = useTrans('otr.permanent_flex_field');

  if (field.data_type === 'TEXT') {
    return (
      <>
        <Label htmlFor={field.id} label={t(field.field_code)} {...(field.is_mandatory && { isRequired: true })} />
        {skeleton ? (
          <InputSkeleton />
        ) : (
          <Input value={value} onChange={(e: any) => onChange(e.target.name, e.target.value)} className={`form-control error-${field.id}`} id={field.id} name={field.id} />
        )}
      </>
    );
  } else if (field.data_type === 'DATE') {
    return (
      <>
        <Label htmlFor={field.id} label={t(field.field_code)} {...(field.is_mandatory && { isRequired: true })} />
        {skeleton ? (
          <InputSkeleton />
        ) : (
          <Input type="date" value={value} onChange={(e: any) => onChange(e.target.name, e.target.value)} className={`form-control error-${field.id}`} id={field.id} name={field.id} />
        )}
      </>
    );
  } else {
    return null;
  }
};

export const FlexField = ({ field, value, onChange, skeleton = false }: { field: IFlexField; value: any; onChange: Function; skeleton?: boolean }) => {
  return <>{renderFieldElement(field, value, onChange, skeleton)}</>;
};

async function getOne(entity: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/flex-fields/config/${entity}`,
      method: 'GET',
    }),
  );
}
