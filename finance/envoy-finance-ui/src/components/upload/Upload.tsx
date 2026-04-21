'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Input, Skeleton } from '@apptimus-ui/ui-element';
import { useRouter } from 'next/navigation';
import React, { useEffect, useState } from 'react';
// import PreviewList from './tabs/PreviewList';
import Summary from './tabs/Summary';
import Mapping from './tabs/Mapping';
import EditMapping from './tabs/EditMapping';
import { toaster } from '@/helpers/services/toaster';
import PreviewTable from './tabs/PreviewTable';
import { ExcelMappingResponse } from '@/helpers/services/excelUploadCommonService';
import GoBack from '../others/page-related/GoBack';
import FileDownloadButton from '../others/page-related/uploader/FileDownloadButton';
import { getPaymentImportTemplate } from '@/app/finance/a/payments/_utils/api-service';

interface UploadProps {
  type: 'payments' | 'commission_setup';
  backUrl: string;
  title: string;
  mappingFields: string[];
  onFileUpload: (file: File) => Promise<any>;
  onMappingSubmit: (mapping: any) => Promise<any>;
  onPreviewSubmit: (data: any) => Promise<any>;
  isAllRequired?: boolean;
}

function Upload({ type, backUrl, title, mappingFields, onFileUpload, onMappingSubmit, onPreviewSubmit, isAllRequired = true }: UploadProps) {
  const router = useRouter();
  const t = useTrans('label.invoice,otr.common,be.msg');
  const [currentTabId, setCurrentTabId] = useState(1);
  const [_resource, setResource] = useState<File | null>(null);
  const [_mappingData, setMappingData] = useState<any>(null);
  const [previewData, setPreviewData] = useState<any>(null);
  const [fileError, setFileError] = useState<string>('');
  const [excelData, setExcelData] = useState<ExcelMappingResponse | undefined>(undefined);
  const [previewRows, setPreviewRows] = useState<any[]>([]);
  const [editRowId, setEditRowId] = useState<string | null>(null);
  const [editRowData, setEditRowData] = useState<any>(null);
  const [mapping, setMapping] = useState<any>({});
  const [flexFields, setFlexFields] = useState<any[]>([]);
  const [skeleton, setSkeleton] = useState(true);
  const [templateUrl, setTemplateUrl] = useState<string>('');

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getPaymentImportTemplate();
      if (responseData?.is_success) {
        setTemplateUrl(responseData.result?.s3_url || '');
        setSkeleton(false);
      }
    };
    fetchData();
  }, []);

  const steps = [
    { id: 1, title: t('upload_file') },
    { id: 2, title: t('mapping') },
    { id: 3, title: t('preview') },
    { id: 4, title: t('summary') },
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
      setMappingData(null);
      setExcelData(undefined);
      setPreviewData(null);
      setResource(file);

      try {
        const response = await onFileUpload(file);
        if (response.success) {
          setExcelData(response);
          setPreviewData(response);
          setCurrentTabId(2);
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
        setMappingData(null);
        setExcelData(undefined);
        setPreviewData(null);
        setResource(null);
      }
    } else {
      router.push(backUrl);
    }
  };

  // Regenerate previewRows when mapping or excelData changes
  const regeneratePreviewRows = (mappingObj: any, flexFieldsArr: any[], excelDataObj: ExcelMappingResponse | undefined) => {
    if (!excelDataObj?.result?.rows) return [];
    const rows = excelDataObj.result.rows.map((row: any) => {
      const mappedRow: any = {
        row_id: row['0'],
        flex_fields: {},
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
      // Flex fields
      flexFieldsArr.forEach((field: any) => {
        const headerIndex = excelDataObj.result.headers.findIndex((h) => h.value.toString() === field.dataValue);
        if (headerIndex !== -1) {
          mappedRow.flex_fields[field.name.toLowerCase().replace(/\s+/g, '_')] = row[headerIndex.toString()];
        }
      });
      return mappedRow;
    });
    return rows;
  };

  // Handle mapping change
  const handleMappingChange = (data: any) => {
    setMapping(data.mappings);
    setFlexFields(data.flexFields);
    const rows = regeneratePreviewRows(data.mappings, data.flexFields, excelData);
    setPreviewRows(rows);
  };

  // Handle edit row
  const handleEditRow = (rowId: string) => {
    const row = previewRows.find((r) => r.row_id === rowId);
    setEditRowId(rowId);
    setEditRowData(row);
  };

  // Handle save edit
  const handleSaveEdit = (editedRow: any) => {
    setPreviewRows((prevRows) => prevRows.map((row) => (row.row_id === editedRow.row_id ? editedRow : row)));
    setEditRowId(null);
    setEditRowData(null);
  };

  const handleNextPage = async () => {
    if (currentTabId === 1) {
      if (!_resource) {
        setFileError('Please select a file to continue');
        return;
      }
      setCurrentTabId(2);
      return;
    }
    if (currentTabId === 2) {
      // Check if all required fields are mapped
      const unmappedFields = mappingFields.filter((field) => !mapping[field]);
      if (unmappedFields.length > 0 && isAllRequired) {
        return;
      }
      setCurrentTabId(3);
      return;
    }
    if (currentTabId === 3) {
      // Submit to API for both types
      try {
        const dataToSend = previewRows.map((row) => ({
          ...row,
          insurer_invoice_id: row.insurer_invoice_id !== undefined && row.insurer_invoice_id !== null && row.insurer_invoice_id !== '' ? parseInt(row.insurer_invoice_id, 10) : undefined,
        }));
        const mappingPayload = {
          mapping: Object.entries(mapping).map(([systemField, excelField]) => ({
            system_field_name: systemField,
            excel_field_name: excelField,
          })),
          flex_fields: flexFields.map((field: any) => ({
            key: field.name.toLowerCase().replace(/\s+/g, '_'),
            excel_field: field.dataValue,
          })),
          data: dataToSend,
          type: type,
          file_name: _resource?.name || '',
        };
        const response = await onMappingSubmit(mappingPayload);
        if (response.is_success || response.success) {
          setPreviewData(response);
          setCurrentTabId(4); // Always go to summary for both types
        } else {
          toaster.error(response.message || 'Failed to submit mapping');
        }
      } catch (error) {
        console.error('Failed to submit mapping');
      }
      return;
    }
    if (currentTabId === 4 && previewData) {
      try {
        await onPreviewSubmit(previewData);
        if (type === 'payments') {
          router.push('/finance/a/payments');
        } else {
          router.push('/finance/a/commission-setup');
        }
      } catch (error) {
        console.error('Error submitting preview:', error);
        toaster.error('Failed to submit preview');
      }
      return;
    }
    if (currentTabId < steps.length) {
      setCurrentTabId(currentTabId + 1);
    }
  };

  return (
    <>
      <GoBack goTo={() => router.push(backUrl)} title={title} />
      <div className="card-body bg-white p-3 rounded-3 mb-3">
        <ul className="d-flex justify-content-center gap-5 list-unstyled mb-0 crm-recent-activity">
          {steps.map((step, index) => (
            <li key={index} className="crm-recent-activity-content">
              <div className="align-items-center">
                <div className="d-flex justify-content-center me-3">
                  {step.id <= currentTabId ? (
                    <>
                      <span className={`avatar avatar-xs bg-primary-transparent avatar-rounded`}>
                        <Flexicon icon="check-circle" variant="solid" size={50} />
                      </span>
                    </>
                  ) : (
                    <>
                      <span className="avatar claim-avatar claim-transparent claim-avatar-rounded">
                        <i className="bi bi-circle-fill fs-8"></i>
                      </span>
                    </>
                  )}
                </div>
                <div className="mt-2">
                  <div className="fw-medium mb-1 fs-12">{step.title}</div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
      {currentTabId === 1 && type === 'payments' && (
        <div className="panel">
          <div className="fs-15 fw-semibold mb-3">{t('download_template')}</div>
          {skeleton ? <Skeleton height="20px" width="50%" /> : <FileDownloadButton s3Key={templateUrl} fileType="excel" />}
        </div>
      )}
      {currentTabId === 1 && (
        <div className="panel">
          <div className="fs-15 fw-semibold mb-3">{t('upload_payment_data_file')}</div>
          <div className="col-12 col-md-12 mb-3">
            <Input label={t('select_file')} isRequired type="file" onChange={(e: any) => handleFileChange(e)} className="form-control error-invoice_document" name="invoice_document" />
            {fileError && <div className="text-danger mt-2">{fileError}</div>}
          </div>
        </div>
      )}
      {currentTabId === 2 && (
        <Mapping
          fields={mappingFields}
          onMappingChange={handleMappingChange}
          excelData={excelData}
          onNext={() => handleNextPage()}
          isAllRequired={isAllRequired}
          mapping={mapping}
          setMapping={setMapping}
        />
      )}
      {currentTabId === 3 && <PreviewTable rows={previewRows} fields={mappingFields.filter((field) => mapping[field])} flexFields={flexFields} onEditRow={handleEditRow} />}
      {currentTabId === 4 && <Summary data={previewData} />}

      <div className="d-flex justify-content-start gap-2 mt-3">
        <Button color="light" className="d-flex align-items-center gap-1" onClick={() => onBack()}>
          <Flexicon icon="chevron-left" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('back')}</span>
        </Button>
        {currentTabId === 4 ? (
          <Button color="primary" text={t('done')} onClick={handleNextPage} />
        ) : (
          <Button color="primary" className="d-flex align-items-center gap-1" onClick={handleNextPage}>
            <span className="d-none d-sm-inline">{t('next')}</span>
            <Flexicon icon="chevron-right" variant="line" size={18} />
          </Button>
        )}
      </div>
      {editRowId && editRowData && (
        <EditMapping isOpen={!!editRowId} rowData={editRowData} fields={mappingFields} flexFields={flexFields} onSave={handleSaveEdit} onCancel={() => setEditRowId(null)} />
      )}
    </>
  );
}

export default Upload;
