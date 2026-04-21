import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Select } from '@apptimus-ui/select';
import { Button, Label, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { getAllVendorQuotation, updateShortList } from '../../../api-service';
import { fetchAllCriteria } from '../../../service';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { toaster } from '@/helpers/services/toaster';
import { ICompareData } from '../../../model';
import { thousandSeparator } from '@/helpers/services/commonService';

function CompareQuotations({ isOpen, onCancel, selectedIds, onSubmit, quotationId }: { isOpen: boolean; onCancel: Function; selectedIds: string[]; onSubmit: Function; quotationId: string }) {
  const t = useTrans('label.quotations,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [criteria, setCriteria] = useState<{ title: string; column: string; id: string }[]>([]);
  const [stickyIds, setStickyIds] = useState<string[]>([]);
  const [data, setData] = useState<ICompareData[]>([]);
  const [stickedData, setStickedData] = useState<ICompareData[]>([]);
  const [nonStickedData, setNonStickedData] = useState<ICompareData[]>([]);
  const [shortListIds, setShortListIds] = useState<string[]>([]);
  const [skeleton, setSkeleton] = useState(false);
  const [defaultValue, setDefaultValue] = useState();
  const [allCriteria, setAllCriteria] = useState<{ title: string; column: string }[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getAllVendorQuotation({ ids: selectedIds.join(','), filter: 'received' }, quotationId);

      if (responseData?.is_success) {
        const data = responseData.result;
        setData(data);
        const criteriaData = await fetchAllCriteria();
        setAllCriteria(criteriaData);
        const requiredTitles = ['version', 'received_date', 'expiry_date', 'total_amount'];
        const filterValues = criteriaData.filter((item: any) => requiredTitles.includes(item.column));
        setCriteria(filterValues);
        setDefaultValue(filterValues);
        setSkeleton(false);
      }
    };

    if (selectedIds.length > 0) {
      setSkeleton(true);
      fetchData();
    }
  }, [selectedIds]);

  useEffect(() => {
    const selectedData = data.filter((item) => stickyIds.includes(item.vendor_quotation_id));
    setStickedData(selectedData);
    const excludedData = data.filter((item) => !stickyIds.includes(item.vendor_quotation_id));
    setNonStickedData(excludedData);
  }, [stickyIds, criteria, data]);

  const handleStickyCard = (id: string) => {
    if (stickyIds.includes(id)) {
      setStickyIds((prevValue) => prevValue.filter((item) => item !== id));
    } else {
      setStickyIds((prevValue) => [...prevValue, id]);
    }
  };

  const handleShortList = async (id: string) => {
    if (shortListIds.includes(id)) {
      const response = await updateShortList(id, { is_shortlisted: 'no' });
      if (response.is_success) {
        setShortListIds((prevValue) => prevValue.filter((item) => item !== id));
        toaster.success(tBe(response.message));
      }
    } else {
      const response = await updateShortList(id, { is_shortlisted: 'yes' });
      if (response.is_success) {
        setShortListIds((prevValue) => [...prevValue, id]);
        toaster.success(tBe(response.message));
      }
    }
  };

  const getComparisonColor = (column: string, value: any) => {
    if (column !== 'total_amount') return '';
    if (!value || value === '-') return '';

    const allValues = data.map((item) => (item as any)[column] || item.document_extracted_details?.[column]).filter((v) => v && v !== '-');

    if (allValues.length <= 1) return '';

    const isSame = allValues.every((v) => v === allValues[0]);
    return isSame ? '#e6f9ed' : '#fff4e5'; // Light green for same, light orange for different
  };

  const renderCriteriaValue = (company: ICompareData, column: string) => {
    const value = (company as any)[column] || company.document_extracted_details?.[column];
    const bgColor = getComparisonColor(column, value);

    if (!value || (Array.isArray(value) && value.length === 0)) return '-';

    const content = (() => {
      if (column === 'total_amount') {
        return thousandSeparator(value);
      }

      if (Array.isArray(value)) {
        const filteredItems = value.filter((item: any) => {
          if (typeof item === 'object' && item !== null) {
            return Object.values(item).some((val) => val !== '' && val !== null && val !== undefined);
          }
          return item !== '' && item !== null && item !== undefined;
        });

        if (filteredItems.length === 0) return '-';

        return (
          <div className="text-start px-2">
            {filteredItems.map((item: any, idx: number) => {
              if (typeof item === 'object' && item !== null) {
                const entries = Object.entries(item).filter(([_, v]) => v !== '' && v !== null && v !== undefined);
                if (entries.length === 0) return null;

                if (entries.length === 2 && typeof entries[0][1] === 'string' && typeof entries[1][1] === 'string') {
                  return (
                    <div key={idx} className="mb-1">
                      <span className="fw-semibold">{entries[0][1]}:</span> {entries[1][1]}
                    </div>
                  );
                }
                return (
                  <div key={idx} className="mb-2">
                    {entries.map(([key, val]: [string, any], i) => (
                      <div key={i}>
                        <span className="fw-semibold">{key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}:</span> {val || '-'}
                      </div>
                    ))}
                  </div>
                );
              }
              return <div key={idx}>{item}</div>;
            })}
          </div>
        );
      }

      if (typeof value === 'object' && value !== null) {
        const entries = Object.entries(value).filter(([_, val]) => val !== '' && val !== null && val !== undefined);
        if (entries.length === 0) return '-';

        return (
          <ul className="text-start ps-4 mb-0">
            {entries.map(([key, val]: [string, any], idx) => (
              <li key={idx} className="mb-1">
                <span className="fw-semibold">{key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}:</span> {val}
              </li>
            ))}
          </ul>
        );
      }

      return value;
    })();

    return <div style={{ backgroundColor: bgColor, width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>{content}</div>;
  };

  return (
    <Modal isOpen={isOpen} size="fullscreen" scrollable>
      <ModalHeader title={t('compare_quotations')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="bg-light rounded-1 p-4" style={{ height: '100vh', overflow: 'auto', scrollbarWidth: 'none' }}>
          <div className="panel-title">{t('define_key_comparison_criteria')}</div>
          <div className="row" id={`${form.quotation.store}`}>
            <div className="col-12 col-md-6 mb-3 custom-select compare-criteria">
              <Label label={t('define_key_comparison_criteria_from_quotations')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Select
                  onChange={(_value: any, data: any) => setCriteria(data)}
                  className="form-control error-customer_id"
                  option={{ label: 'title', value: 'column' }}
                  multiple
                  isSearchable={true}
                  options={allCriteria}
                  defaultValue={defaultValue}
                />
              )}
            </div>
            {!skeleton && (
              <div className="col-12 col-md-6 mb-3 d-flex align-items-end justify-content-end gap-3 pb-2">
                <div
                  className="d-flex align-items-center gap-2 px-3 py-1 rounded-pill border"
                  style={{ backgroundColor: '#e6f9ed', borderColor: '#b2f2bb !important', fontSize: '12px', color: '#099268' }}
                >
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#099268' }} />
                  {t('same_across_all_insurers')}
                </div>
                <div
                  className="d-flex align-items-center gap-2 px-3 py-1 rounded-pill border"
                  style={{ backgroundColor: '#fff4e5', borderColor: '#ffe8cc !important', fontSize: '12px', color: '#d9480f' }}
                >
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#d9480f' }} />
                  {t('differs_between_insurers')}
                </div>
              </div>
            )}
          </div>
          {skeleton ? (
            <Skeleton width="735px" height="200px" />
          ) : (
            <div className="mt-4">
              <div
                className="compare-card d-grid"
                style={{
                  gridTemplateColumns: `minmax(180px, 1fr) repeat(${data.length}, minmax(280px, 1fr))`,
                  gridAutoRows: 'min-content',
                  gap: '0 8px',
                }}
              >
                {/* Criteria Titles Column */}
                <div style={{ display: 'contents' }}>
                  <div className="position-sticky start-0 bg-light z-3" style={{ gridRow: 1 }}>
                    <div className="card rounded-0 shadow-sm text-center h-100 mb-0 border-bottom-0">
                      <div className="compare-card-header d-flex justify-content-center align-items-center">
                        <div className="fw-semibold text">{t('criteria')}</div>
                      </div>
                    </div>
                  </div>
                  {criteria.map((cri, index) => (
                    <div key={`title-${index}`} className="position-sticky start-0 bg-light z-3" style={{ gridRow: index + 2 }}>
                      <div className="list-group-item compare-list text-center text-muted py-3 rounded-0 border-top-0 border-bottom h-100">{cri.title}</div>
                    </div>
                  ))}
                  <div className="position-sticky start-0 bg-light z-3" style={{ gridRow: criteria.length + 2 }}>
                    <div className="list-group-item compare-list border-0 h-100 bg-transparent" />
                  </div>
                </div>

                {/* Sticked Companies Columns */}
                {stickedData.map((company) => (
                  <div key={company.vendor_quotation_id} style={{ display: 'contents' }}>
                    <div style={{ gridRow: 1 }}>
                      <div className="rounded-0 shadow-sm text-center position-relative border border-primary border-bottom-0 bg-white h-100">
                        <div className="compare-card-header position-relative">
                          <Flexicon icon="pin-01" variant="line" className="text-primary pointer position-absolute top-0 end-0 m-2" onClick={() => handleStickyCard(company.vendor_quotation_id)} />
                          <div className="fw-semibold text p-3">{company.service_provider_name}</div>
                        </div>
                      </div>
                    </div>
                    {criteria.map((cri, idx) => (
                      <div key={`sticky-${company.vendor_quotation_id}-${idx}`} style={{ gridRow: idx + 2 }}>
                        <div className="compare-list list-group-item text-muted p-0 rounded-0 border-primary border-start border-end border-top-0 border-bottom h-100 bg-white overflow-hidden">
                          {renderCriteriaValue(company, cri.column)}
                        </div>
                      </div>
                    ))}
                    <div style={{ gridRow: criteria.length + 2 }}>
                      <div className="text-center p-2 border-primary border-start border-end border-bottom bg-white rounded-bottom">
                        <Button
                          text={shortListIds.includes(company.vendor_quotation_id) ? t('added_shortlisted') : t('add_to_shortlist')}
                          onClick={() => handleShortList(company.vendor_quotation_id)}
                          color={shortListIds.includes(company.vendor_quotation_id) ? 'primary' : 'light'}
                          width="sm"
                          className="w-100"
                        />
                      </div>
                    </div>
                  </div>
                ))}

                {/* Non-Sticked Companies Columns */}
                {nonStickedData.map((company) => (
                  <div key={company.vendor_quotation_id} style={{ display: 'contents' }}>
                    <div style={{ gridRow: 1 }}>
                      <div className="card rounded-0 shadow-sm text-center position-relative h-100 mb-0 border-bottom-0">
                        <div className="compare-card-header position-relative">
                          <Flexicon icon="pin-01" variant="line" className="pointer position-absolute top-0 end-0 m-2" onClick={() => handleStickyCard(company.vendor_quotation_id)} />
                          <div className="fw-semibold text p-3">{company.service_provider_name}</div>
                        </div>
                      </div>
                    </div>
                    {criteria.map((cri, idx) => (
                      <div key={`nSticky-${company.vendor_quotation_id}-${idx}`} style={{ gridRow: idx + 2 }}>
                        <div className="compare-list list-group-item text-muted p-0 rounded-0 border-top-0 border-bottom h-100 overflow-hidden">{renderCriteriaValue(company, cri.column)}</div>
                      </div>
                    ))}
                    <div style={{ gridRow: criteria.length + 2 }}>
                      <div className="text-center p-2">
                        <Button
                          text={shortListIds.includes(company.vendor_quotation_id) ? t('added_shortlisted') : t('add_to_shortlist')}
                          onClick={() => handleShortList(company.vendor_quotation_id)}
                          color={shortListIds.includes(company.vendor_quotation_id) ? 'primary' : 'light'}
                          width="sm"
                          className="w-100"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button
            text={t('submit')}
            onClick={() => {
              onSubmit(), onCancel();
            }}
            width="sm"
          />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default CompareQuotations;
