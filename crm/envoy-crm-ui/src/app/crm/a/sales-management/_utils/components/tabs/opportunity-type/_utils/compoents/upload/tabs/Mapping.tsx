import { useTrans } from '@/helpers/services/lang/langService';
import { Select } from '@apptimus-ui/select';
import { Label } from '@apptimus-ui/ui-element';
import React, { useState, useEffect, useMemo } from 'react';
import { useTable } from '@apptimus-ui/table';
import { IExcelMappingResponse } from '../../../model';

interface MappingProps {
  fields: Array<{ id: string; label: string; isRequired: boolean }>;
  onMappingChange: (mapping: any) => void;
  excelData?: IExcelMappingResponse;
  mappingData: Record<string, string>;
  setMappingData: any;
  errors: any;
}

function Mapping({ fields, onMappingChange, excelData, mappingData, setMappingData, errors }: MappingProps) {
  const t = useTrans('label.sales_managements,otr.common,be.msg');
  const [usedExcelFields, setUsedExcelFields] = useState<Set<string>>(new Set());

  useEffect(() => {
    // Reset used fields when excel data changes
    setUsedExcelFields(new Set());
    setMappingData({});
  }, [excelData]);

  const handleMappingChange = (fieldId: string, value: any) => {
    const newMapping = { ...mappingData };
    const oldValue = mappingData[fieldId];

    // Remove old value from used fields
    if (oldValue) {
      setUsedExcelFields((prev) => {
        const newSet = new Set(prev);
        newSet.delete(oldValue);
        return newSet;
      });
    }

    // Add new value to used fields
    if (value) {
      setUsedExcelFields((prev) => {
        const newSet = new Set(prev);
        newSet.add(value);
        return newSet;
      });
    }

    newMapping[fieldId] = value;
    setMappingData(newMapping);
    onMappingChange({ mappings: newMapping });
  };

  const getExcelFieldOptions = () => {
    if (!excelData?.result?.headers) return [];
    return excelData.result.headers
      .filter((header) => !usedExcelFields.has(header.value.toString()))
      .map((header) => ({
        label: header.value.toString(),
        value: header.value.toString(),
      }));
  };

  const tableData = useMemo(() => {
    return fields.map((field) => ({
      form_field_name: field.label,
      form_is_required: field.isRequired,
      id: field.id,
    }));
  }, [fields]);

  const columns = useMemo(
    () => [
      {
        header: t('form_field_name'),
        accessorKey: 'form_field_name',
        accessorFn: (row: any) => <Label label={row.form_field_name} isRequired={row.form_is_required} />,
      },
      {
        header: t('excel_field_name'),
        accessorKey: 'excel_field_name',
        size: '15rem',
        cell: (cell: any) => {
          // Safely get the field id
          const fieldId = cell?.cell?.id;
          if (!fieldId) return null;

          return (
            <div key={cell.id} className="custom-select">
              <Select
                key={mappingData?.[fieldId] || ''}
                defaultValue={mappingData?.[fieldId] ? { label: mappingData[fieldId], value: mappingData[fieldId] } : undefined}
                onChange={(value: any) => {
                  handleMappingChange(fieldId, value);
                }}
                className={`form-control  ${errors[fieldId] ? 'is-invalid' : ''}`}
                option={{
                  label: 'label',
                  value: 'value',
                }}
                options={getExcelFieldOptions()}
                isSearchable={true}
              />
            </div>
          );
        },
      },
    ],
    [t, mappingData, errors, getExcelFieldOptions],
  );

  const tableProperties = useTable({
    columns,
    data: tableData,
  });
  return (
    <div className="bg-white custom-card p-3 rounded-3 mb-3">
      <div className="fs-15 fw-semibold">{t('mapping_risk_details_from_external_file')}</div>
      <div className="col-lg-12">
        <div className="mt-3">{tableProperties.Table as React.ReactNode}</div>
      </div>
    </div>
  );
}

export default Mapping;
