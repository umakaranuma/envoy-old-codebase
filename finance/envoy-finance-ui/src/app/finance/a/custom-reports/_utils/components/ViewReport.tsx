'use client';
import GoBack from '@/components/others/page-related/GoBack';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import ReportTable from './view/ReportTable';
import { getExportedReportUrl, getOneReportData } from '../api-service';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import CreateChart from './view/CreateChart';
import ReportChart from './view/ReportChart';
import EditChart from './view/EditChart';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';
// import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { initExcelFormData, initPDFFormData } from '../model';
import { generateHtml } from '@/helpers/services/commonService';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';

function ViewReport() {
  const t = useTrans('label.custom_report,otr.common,be.msg');
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const { setCustomBreadcrumb } = useBreadcrumb();
  const reportId = params.reportId?.toString() || '';
  const [tableColumns, setTableColumns] = useState([]);
  const [tab, setTab] = useState('table');
  const [isChartOpen, setIsChartOpen] = useState(false);
  const [tableVersion, setTableVersion] = useState(0);
  const [currentEditId, setCurrentEditId] = useState('');
  const [loading, setLoading] = useState(false);
  const [excelFormData, setExcelFormData] = useState(initExcelFormData);
  const [pdfFormData, setPdfFormData] = useState(initPDFFormData);

  useEffect(() => {
    setCustomBreadcrumb({
      text: t('view'),
      backurl: '/finance/a/custom-reports',
    });
    return () => setCustomBreadcrumb(null);
  }, [setCustomBreadcrumb]);

  useEffect(() => {
    const tab = searchParams.get('t') || 'table';
    toggleTableTab(tab);
  }, []);

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    router.push(`/finance/a/custom-reports/${reportId}?t=${activeTab}`, { scroll: false });
  };

  useEffect(() => {
    if (reportId) {
      fetchTableColumn();
    }
  }, [reportId]);

  const fetchTableColumn = async () => {
    setLoading(true);
    const response = await getOneReportData({}, reportId);
    console.log('response column ', response);

    if (response.is_success) {
      const fields = response.result.data.json.fields;
      const skipColumnData = response.result.data.json.skip_columns || [];
      const skipCodes = new Set(skipColumnData.map((c: any) => c.code));
      console.log('skipCodes:', skipCodes);

      setExcelFormData({ ...initExcelFormData, report_id: reportId, type: 'excel', json_data: [{ title: 'Report', data: response.result.data.data }] });
      setPdfFormData({ ...initPDFFormData, report_id: reportId, type: 'pdf', html_content: generateHtml(response.result.data.data) });
      // filter out fields whose code is in skipCodes
      const data = fields.filter((field: any) => !skipCodes.has(field.code));

      const columns = data.map((field: any) => ({
        id: field.code,
        header: field.label,
        accessorKey: field.label,
        sort: true,
      }));
      setTableColumns(columns);
      setLoading(false);
    }
  };

  const handleExcelExport = async () => {
    try {
      // Generate new Excel file
      const response = await getExportedReportUrl(excelFormData);
      // Download the file
      window.open(response.result.download_url, '_blank');
    } catch (error) {
      console.error('Excel generation failed:', error);
    }
  };

  const handlePDFExport = async () => {
    try {
      // Generate new Excel file
      const response = await getExportedReportUrl(pdfFormData);
      // Download the file
      if (response.is_success && response.result?.download_url) {
        window.open(response.result.download_url, '_blank');
      } else {
        console.error('PDF generation failed or download URL missing', response);
      }
    } catch (error) {
      console.error('Excel generation failed:', error);
    }
  };

  return (
    <>
      <div className="d-flex justify-content-between align-items-center">
        <GoBack goTo={() => router.push('/finance/a/custom-reports')} title={t('custom_report')} />
        <div className="d-flex gap-2">
          <Dropdown
            trigger={
              <Button className="d-flex align-items-center gap-1">
                <Flexicon icon="upload-01" variant="line" size={15} />
                <span className="d-none d-sm-inline">{t('export_report')}</span>
                <Flexicon icon="chevron-down" variant="line" size={18} />
              </Button>
            }
          >
            {(onClose: Function) => (
              <>
                <DropdownItem onClick={() => (handleExcelExport(), onClose())}>
                  <span>{t('excel')}</span>
                </DropdownItem>
                <DropdownItem onClick={() => (handlePDFExport(), onClose())}>
                  <span>{t('pdf')}</span>
                </DropdownItem>
              </>
            )}
          </Dropdown>
          <Button className="d-flex align-items-center gap-1" onClick={() => setIsChartOpen(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('create_chart')}</span>
          </Button>
        </div>
      </div>
      <div className="panel">
        <div className="il-box-tab">
          <div className={`il-box-tab-item ${tab === 'table' ? 'active' : ''}`} onClick={() => toggleTableTab('table')}>
            {t('table')}
          </div>
          <div className={`il-box-tab-item ${tab === 'chart' ? 'active' : ''}`} onClick={() => toggleTableTab('chart')}>
            {t('chart')}
          </div>
        </div>
        {tableColumns && tab === 'table' && <ReportTable reportId={reportId} tableColumns={tableColumns} loading={loading} />}
        {tab === 'chart' && <ReportChart reportId={reportId} tableVersion={tableVersion} onEdit={(id) => setCurrentEditId(id)} />}
      </div>
      {isChartOpen && (
        <CreateChart
          isOpen={isChartOpen}
          onClose={() => setIsChartOpen(false)}
          afterSave={() => {
            setIsChartOpen(false);
            setTableVersion(tableVersion + 1);
          }}
          reportId={reportId}
        />
      )}
      {currentEditId && (
        <EditChart
          isOpen={!!currentEditId}
          onClose={() => setCurrentEditId('')}
          afterSave={() => {
            setCurrentEditId('');
            setTableVersion(tableVersion + 1);
          }}
          editId={currentEditId}
          reportId={reportId}
        />
      )}
    </>
  );
}

export default ViewReport;
