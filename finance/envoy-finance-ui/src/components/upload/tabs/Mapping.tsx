import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Select } from '@apptimus-ui/select';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { useState, useEffect, useMemo } from 'react';
import CreateField from '../CreateField';
import { ExcelMappingResponse, FlexField } from '@/helpers/services/excelUploadCommonService';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';

interface MappingProps {
  fields: string[];
  onMappingChange: (mapping: any) => void;
  excelData?: ExcelMappingResponse;
  onNext: () => void;
  isAllRequired?: boolean;
  mapping: Record<string, string>;
  setMapping: React.Dispatch<React.SetStateAction<Record<string, string>>>;
}

function Mapping({ fields, onMappingChange, excelData, isAllRequired, mapping, setMapping }: MappingProps) {
  const t = useTrans('label.invoice,otr.common,be.msg');
  const [createFormVisible, setCreateFormVisible] = useState(false);
  // const [mapping, setMapping] = useState<Record<string, string>>({});
  const [flexFields, setFlexFields] = useState<FlexField[]>([]);
  const [usedExcelFields, setUsedExcelFields] = useState<Set<string>>(new Set());
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateMapping = (currentMapping: Record<string, string>) => {
    const newErrors: Record<string, string> = {};
    const unmappedFields: string[] = [];

    fields.forEach((field) => {
      if (!currentMapping[field]) {
        newErrors[field] = t('field_required');
        unmappedFields.push(field);
      }
    });

    setErrors(newErrors);
    return unmappedFields.length === 0;
  };

  useEffect(() => {
    // Validate mapping whenever it changes
    validateMapping(mapping);
  }, [mapping]);

  const handleMappingChange = (field: string, value: any) => {
    const newMapping = { ...mapping };
    const oldValue = mapping[field];

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

    newMapping[field] = value;
    setMapping(newMapping);
    onMappingChange({ mappings: newMapping, flexFields });
  };

  const handleRemoveMapping = (field: string) => {
    const newMapping = { ...mapping };
    const oldValue = mapping[field];

    // Remove from used fields
    if (oldValue) {
      setUsedExcelFields((prev) => {
        const newSet = new Set(prev);
        newSet.delete(oldValue);
        return newSet;
      });
    }

    // Remove the mapping
    delete newMapping[field];
    setMapping(newMapping);
    onMappingChange({ mappings: newMapping, flexFields });
  };

  const handleFlexFieldAdd = (field: FlexField) => {
    const newFlexFields = [...flexFields, field];
    setFlexFields(newFlexFields);
    onMappingChange({ mappings: mapping, flexFields: newFlexFields });
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

  // Create mapping table data
  const mappingTableData = useMemo(() => {
    return fields.map((field) => ({
      id: field,
      systemField: field,
      excelField: mapping[field] || '',
      error: errors[field] || '',
    }));
  }, [fields, mapping, errors]);

  // Create flex fields table data
  const flexFieldsTableData = useMemo(() => {
    return flexFields.map((field, index) => ({
      id: `${field.name}-${index}`,
      fieldName: field.name,
      dataType: field.dataType,
      dataValue: field.dataValue,
    }));
  }, [flexFields]);

  // Mapping table columns
  const mappingColumns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'systemField',
        header: t('system_field_name'),
        accessorKey: 'systemField',
        sort: false,
        cell: ({ cell }: { cell: any }) => <Label label={cell.getValue()} isRequired={isAllRequired === undefined ? true : isAllRequired} />,
      },
      {
        id: 'excelField',
        header: t('excel_field_name'),
        accessorKey: 'excelField',
        sort: false,
        cell: ({ cell }: { cell: any }) => {
          const field = cell.systemField;
          const currentValue = mapping[field];
          const fieldError = errors[field];

          return (
            <div className="custom-select position-relative">
              <Select
                key={currentValue || ''}
                defaultValue={currentValue ? { label: currentValue, value: currentValue } : undefined}
                onChange={(value) => handleMappingChange(field, value)}
                className={`form-control ${fieldError && isAllRequired === undefined ? true : isAllRequired ? 'is-invalid' : ''}`}
                option={{ label: 'label', value: 'value' }}
                isSearchable={true}
                options={getExcelFieldOptions()}
              />
              {currentValue && (
                <button
                  type="button"
                  className="btn btn-link position-absolute"
                  style={{ right: '30px', top: '50%', transform: 'translateY(-50%)', padding: '0', color: '#dc3545' }}
                  onClick={() => handleRemoveMapping(field)}
                >
                  <Flexicon icon="x-circle" size={18} />
                </button>
              )}
              {fieldError && <div className="invalid-feedback">{fieldError}</div>}
            </div>
          );
        },
      },
    ],
    [mapping, errors, t, getExcelFieldOptions, handleMappingChange, handleRemoveMapping],
  );

  // Flex fields table columns
  const flexFieldsColumns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'fieldName',
        header: t('field_name'),
        accessorKey: 'fieldName',
        sort: false,
      },
      {
        id: 'dataType',
        header: t('data_type'),
        accessorKey: 'dataType',
        sort: false,
      },
      {
        id: 'dataValue',
        header: t('data_value'),
        accessorKey: 'dataValue',
        sort: false,
      },
      {
        id: 'action',
        header: t('action'),
        accessorKey: 'action',
        sort: false,
        cell: ({ row }: { row: any }) => (
          <div className="text-center">
            <button
              type="button"
              className="btn btn-link"
              style={{ padding: '0', color: '#dc3545' }}
              onClick={() => {
                const newFlexFields = flexFields.filter((_, i) => i !== row.index);
                setFlexFields(newFlexFields);
                onMappingChange({ mappings: mapping, flexFields: newFlexFields });
              }}
            >
              <Flexicon icon="x-circle" size={18} />
            </button>
          </div>
        ),
      },
    ],
    [flexFields, mapping, t, onMappingChange],
  );

  // Mapping table properties
  const mappingTableProperties = useAsyncTable({
    columns: mappingColumns,
    loadData: () => Promise.resolve({ data: mappingTableData, dataLength: mappingTableData.length }),
    paginate: false,
    rowSelection: false,
  });

  // Flex fields table properties
  const flexFieldsTableProperties = useAsyncTable({
    columns: flexFieldsColumns,
    loadData: () => Promise.resolve({ data: flexFieldsTableData, dataLength: flexFieldsTableData.length }),
    paginate: false,
    rowSelection: false,
  });

  // Reload tables when data changes
  useEffect(() => {
    mappingTableProperties.reload();
  }, [mappingTableData]);

  useEffect(() => {
    flexFieldsTableProperties.reload();
  }, [flexFieldsTableData]);

  return (
    <div className="bg-white custom-card p-3 rounded-3 mb-3">
      <div className="fs-15 fw-semibold">{t('mapping_payment_from_external_file')}</div>
      <div className="d-flex justify-content-end align-items-center mb-3">
        <Button className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)} size="md" color="primary">
          <Flexicon icon="plus-circle" size={18} />
          <span className="d-none d-sm-inline">{t('add_new')}</span>
        </Button>
      </div>

      <div className="col-lg-12">
        <div className="data-table-container card custom-card">
          <Table tableProperties={mappingTableProperties} recordControl={false} searchOption={false} />
        </div>
      </div>

      {flexFields.length > 0 && (
        <div className="mt-4">
          <h6>{t('flex_fields')}</h6>
          <div className="data-table-container card custom-card">
            <Table tableProperties={flexFieldsTableProperties} recordControl={false} searchOption={false} />
          </div>
        </div>
      )}

      {createFormVisible && <CreateField isOpen={createFormVisible} onCancel={() => setCreateFormVisible(false)} onAdd={handleFlexFieldAdd} excelFields={getExcelFieldOptions()} />}
    </div>
  );
}

export default Mapping;
