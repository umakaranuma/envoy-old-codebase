'use client';

import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Input } from '@apptimus-ui/ui-element';
import { useRouter } from 'next/navigation';
import React, { useState } from 'react';
import EditMapping from './tabs/EditMapping';
import { toaster } from '@/helpers/services/toaster';
import PreviewTable from './tabs/PreviewTable';
import FormStepper from '@/components/others/common/forms/FormStepper';
import Mapping from './tabs/Mapping';
import { IExcelMappingResponse } from '../../model';
import GoBack from '@/components/others/page-related/GoBack';

interface UploadProps {
  backUrl: string;
  title: string;
  mappingFields: any[];
  onFileUpload: (file: File) => Promise<any>;
  onMappingSubmit: (mappingData: any) => Promise<any>;
  opportunityId: string;
}

function Upload({ backUrl, title, mappingFields, onFileUpload, onMappingSubmit, opportunityId }: UploadProps) {
  const router = useRouter();
  const t = useTrans('label.sales_managements,otr.common,be.msg');
  const [currentTabId, setCurrentTabId] = useState(1);
  const [resource, setResource] = useState<File | null>(null);
  const [mappingData, setMappingData] = useState<Record<string, string>>({});
  const [fileError, setFileError] = useState<string>('');
  const [excelData, setExcelData] = useState<IExcelMappingResponse | undefined>(undefined);
  const [previewRows, setPreviewRows] = useState<any[]>([]);
  const [editRowId, setEditRowId] = useState<string | null>(null);
  const [editRowData, setEditRowData] = useState<any>(null);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [errors, setErrors] = useState<Record<string, any[]>>({});

  const steps = [
    { id: 1, title: t('upload_file') },
    { id: 2, title: t('mapping') },
    { id: 3, title: t('preview') },
  ];

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setFileError('');
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      const validTypes = ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xls', '.xlsx'];

      if (!validTypes.includes(file.type) && !file.name.match(/\.(xls|xlsx)$/)) {
        setFileError('Please select a valid Excel file (.xls or .xlsx)');
        return;
      }

      // Reset states before new upload
      setMappingData({});
      setExcelData(undefined);
      setResource(file);

      try {
        const response = await onFileUpload(file);
        if (response.success) {
          setExcelData(response);
        } else {
          setFileError(response.message || 'Failed to process file');
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        setFileError('Error uploading file. Please try again.');
        setResource(null);
      }
    }
  };

  const onBack = () => {
    if (currentTabId > 1) {
      setCurrentTabId(currentTabId - 1);
      if (currentTabId === 2) {
        // Reset mapping data when going back from mapping tab
        setMappingData({});
        setExcelData(undefined);
        setResource(null);
      }
    } else {
      router.push(backUrl);
    }
  };

  const validateMapping = (currentMapping: Record<string, string>, fields: Array<{ id: string; label: string; isRequired: boolean }>) => {
    const newErrors: Record<string, any[]> = {};

    fields.forEach((field) => {
      if (field.isRequired && !currentMapping[field.id]) {
        newErrors[field.id] = [
          {
            error_type: 'required',
            tokens: {
              _attribute: field.id,
            },
          },
        ];
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Regenerate previewRows when mapping or excelData changes
  const regeneratePreviewRows = (mappingObj: any, excelDataObj: IExcelMappingResponse | undefined) => {
    if (!excelDataObj?.result?.rows) return [];
    const rows = excelDataObj.result.rows.map((row: any) => {
      const mappedRow: any = {
        row_id: row['0'],
      };
      // System fields
      Object.entries(mappingObj).forEach(([systemField, excelField]) => {
        const headerIndex = excelDataObj.result.headers.findIndex((h) => h.value.toString() === excelField);
        if (headerIndex !== -1) {
          const key = systemField.toLowerCase().replace(/\s+/g, '_');
          const val = row[headerIndex.toString()];
          if (key === 'insurer_invoice_id') {
            mappedRow[key] = val !== undefined && val !== null && val !== '' ? parseInt(val, 10) : undefined;
          } else if (key === 'date') {
            mappedRow[key] = val ? val.split(' ')[0] : undefined;
          } else {
            mappedRow[key] = val;
          }
        }
      });

      return mappedRow;
    });
    return rows;
  };

  // Handle mapping change
  const handleMappingChange = (data: any) => {
    const rows = regeneratePreviewRows(data.mappings, excelData);
    setPreviewRows(rows);
  };

  // Handle edit row
  const handleEditRow = (rowId: string) => {
    const row = previewRows.find((r) => r.row_id === rowId);
    setEditRowId(rowId);
    setEditRowData(row);
  };

  // Handle delete row
  const handleDeleteRow = (rowId: string) => {
    setPreviewRows((prevRows) => prevRows.filter((row) => row.row_id !== rowId));
  };

  // Handle save edit
  const handleSaveEdit = (editedRow: any) => {
    setPreviewRows((prevRows) => prevRows.map((row) => (row.row_id === editedRow.row_id ? editedRow : row)));
    setEditRowId(null);
    setEditRowData(null);
  };

  const handleNextPage = async () => {
    if (currentTabId === 1) {
      if (!resource) {
        setFileError('Please select a file to continue');
        return;
      }
    }
    if (currentTabId === 2) {
      // Check if all required fields are mapped
      const isValid = validateMapping(mappingData, mappingFields);
      if (!isValid) return;
      setCurrentTabId(3);
      return;
    }
    if (currentTabId === 3) {
      // Submit to API for both types
      try {
        const dataToSend = {
          data: previewRows.map((row) => {
            const { row_id, ...rest } = row;
            return { ...rest };
          }),
        };
        setIsFormProcessing(true);
        const response = await onMappingSubmit(dataToSend);
        if (response.is_success || response.success) {
          toaster.success(response.message);
          router.push(`/crm/a/sales-management/${opportunityId}?t=opp-type&f=board`);
        } else {
          toaster.error(response.message || 'Failed to submit mapping');
        }
      } catch (error) {
        console.error('Failed to submit mapping');
      } finally {
        setIsFormProcessing(false);
      }
    }

    if (currentTabId < steps.length) {
      setCurrentTabId(currentTabId + 1);
    }
  };

  return (
    <>
      <GoBack goTo={() => router.push(backUrl)} title={title} />
      <FormStepper steps={steps} currentTabId={currentTabId} />
      {currentTabId === 1 && (
        <div className="bg-white custom-card overflow-hidden p-3 rounded-3 mb-3">
          <div className="fs-15 fw-semibold mb-3">{t('upload_risk_data_file')}</div>
          <div className="col-12 col-md-12 mb-3">
            <Input label={t('select_file')} isRequired type="file" onChange={(e: any) => handleFileChange(e)} className="form-control error-invoice_document" name="invoice_document" />
            {fileError && <div className="text-danger mt-2">{fileError}</div>}
          </div>
        </div>
      )}
      {currentTabId === 2 && <Mapping fields={mappingFields} onMappingChange={handleMappingChange} excelData={excelData} mappingData={mappingData} setMappingData={setMappingData} errors={errors} />}
      {currentTabId === 3 && <PreviewTable rows={previewRows} fields={mappingFields} onEditRow={handleEditRow} handleDeleteRow={handleDeleteRow} />}
      <div className="d-flex justify-content-start gap-2 mt-3">
        <Button color="light" className="d-flex align-items-center gap-1" onClick={() => onBack()}>
          <Flexicon icon="chevron-left" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('back')}</span>
        </Button>
        {currentTabId === 3 ? (
          <Button color="primary" text={t('upload')} onClick={handleNextPage} isLoading={isFormProcessing} />
        ) : (
          <Button color="primary" className="d-flex align-items-center gap-1" onClick={handleNextPage}>
            <span className="d-none d-sm-inline">{t('next')}</span>
            <Flexicon icon="chevron-right" variant="line" size={18} />
          </Button>
        )}
      </div>
      {editRowId && editRowData && <EditMapping isOpen={!!editRowId} rowData={editRowData} fields={mappingFields} onSave={handleSaveEdit} onCancel={() => setEditRowId(null)} />}
    </>
  );
}

export default Upload;
