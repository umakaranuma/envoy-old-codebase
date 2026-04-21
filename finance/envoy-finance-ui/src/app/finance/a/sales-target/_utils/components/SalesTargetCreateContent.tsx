'use client';
import React, { FormEvent, useEffect, useState } from 'react';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect, Select } from '@apptimus-ui/select';
import { Flexicon } from '@apptimus-ui/flexicon';
import FreeTextSearchInput from './FreeTextSearchInput';
import { fetchAllAgentData, fetchAllSalesTeamData } from '../services';
import { initFormData, years } from '../model';
import { clearError } from '@/helpers/handlers/validationErrorHandler';
import { handle417IndexWiseErrors } from '@/helpers/handlers/indexWiseErrorHandler';
import { form } from '@/constans/Form';
import { createSalesTarget } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import SalesTargetList from './SalesTargetList';

function SalesTargetCreateContent({ selectedType, setCurrentPg }: { selectedType: string; setCurrentPg: (pg: string) => void }) {
  const t = useTrans('label.sales_target,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formDataList, setFormDataList] = useState([{ ...initFormData }]);
  const [formVers, setFormVers] = useState(0);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [activetab, setActiveTab] = useState('');
  const [keywords, setKeywords] = useState<string[]>([]);
  const [agentTableVers, setAgentTableVers] = useState(0);
  const [teamTableVers, setTeamTableVers] = useState(0);
  const [periodVers, setPeriodVers] = useState(0);
  const [errors, setErrors] = useState<Record<number, string[]>>({});

  useEffect(() => {
    setActiveTab(selectedType);
  }, [selectedType]);

  const months = [
    { label: t('january'), value: 1 },
    { label: t('february'), value: 2 },
    { label: t('march'), value: 3 },
    { label: t('april'), value: 4 },
    { label: t('may'), value: 5 },
    { label: t('june'), value: 6 },
    { label: t('july'), value: 7 },
    { label: t('august'), value: 8 },
    { label: t('september'), value: 9 },
    { label: t('october'), value: 10 },
    { label: t('november'), value: 11 },
    { label: t('december'), value: 12 },
  ];

  function handleFormChange(idx: number, field: string, value: any) {
    setFormDataList((prev) => {
      const updated = prev.map((item, i) => (i === idx ? { ...item, [field]: value } : item));

      // If this is a parent entry and agent_id/team_id changed, sync all its children
      if ((field === 'agent_id' || field === 'team_id') && !prev[idx].isTargetSet) {
        return updated.map((item) => {
          // Update target sets that belong to this parent
          if (item.isTargetSet && item.parentIndex === idx) {
            return { ...item, [field]: value };
          }

          return item;
        });
      }

      return updated;
    });
  }

  function addNewColumn() {
    // Create a new entry at the last point
    const newEntry = {
      ...initFormData,
      isNewColumn: true,
    };

    // Add at the very last position of the list
    setFormDataList((prev) => {
      const newList = [...prev, newEntry];
      return newList;
    });
  }

  function removeColumn(idx: number) {
    setFormDataList((prev) => {
      // Find all target sets that belong to this parent
      const children = prev.filter((item, _) => item.isTargetSet && item.parentIndex === idx);

      if (children.length > 0) {
        // If there are children, make the first child the new parent
        const firstChild = children[0];
        const firstChildIndex = prev.findIndex((item, _) => item.isTargetSet && item.parentIndex === idx);

        // Update the first child to be a parent
        const updatedFirstChild = {
          ...firstChild,
          isTargetSet: false,
          parentIndex: undefined,
          isNewColumn: true,
        };

        // Update other children to point to the new parent
        const updatedChildren = children.slice(1).map((child) => ({
          ...child,
          parentIndex: firstChildIndex,
        }));

        // Remove the original parent and all children, then add the updated first child and other children
        const filtered = prev.filter((item, i) => {
          if (i === idx) return false; // Remove original parent
          if (item.isTargetSet && item.parentIndex === idx) return false; // Remove all children
          return true;
        });

        // Insert the updated first child at the original parent position and add other children at the end
        return [...filtered.slice(0, firstChildIndex), updatedFirstChild, ...filtered.slice(firstChildIndex), ...updatedChildren] as any[];
      } else {
        // If no children, just remove the parent
        return prev.filter((_, i) => i !== idx);
      }
    });
  }

  function removeEntireGroup(groupIdx: number) {
    setFormDataList((prev) => {
      // Get all entries in the current group
      const groupedEntries: Array<Array<{ entry: any; cardIdx: number }>> = [];
      let currentGroup: Array<{ entry: any; cardIdx: number }> = [];

      prev.forEach((entry, cardIdx) => {
        if (!entry.isTargetSet) {
          if (currentGroup.length > 0) {
            groupedEntries.push(currentGroup);
          }
          currentGroup = [{ entry, cardIdx }];
        } else {
          currentGroup.push({ entry, cardIdx });
        }
      });

      if (currentGroup.length > 0) {
        groupedEntries.push(currentGroup);
      }

      // Get all indices to remove from the specified group
      const groupToRemove = groupedEntries[groupIdx];
      const indicesToRemove = new Set(groupToRemove.map(({ cardIdx }) => cardIdx));

      // Filter out the entire group
      return prev.filter((_, i) => !indicesToRemove.has(i));
    });
  }

  function addTargetSet(cardIdx: number) {
    const currentEntry = formDataList[cardIdx];
    const currentDate = new Date();
    const currentMonth = currentDate.getMonth() + 1;
    const currentYear = currentDate.getFullYear();

    const newEntry = {
      agent_id: currentEntry.agent_id,
      team_id: currentEntry.team_id,
      period_type: currentEntry.period_type,
      month: currentEntry.period_type === 'monthly' ? currentMonth : null,
      year: currentEntry.period_type === 'yearly' ? currentYear.toString() : currentYear.toString(),
      target_amount: '',
      isTargetSet: true,
      parentIndex: cardIdx,
    };

    // Find the last position of all children for this parent
    let lastChildPosition = cardIdx;
    for (let i = cardIdx + 1; i < formDataList.length; i++) {
      if (formDataList[i].isTargetSet && formDataList[i].parentIndex === cardIdx) {
        lastChildPosition = i;
      } else if (!formDataList[i].isTargetSet) {
        // Found next parent, stop here
        break;
      }
    }

    setFormDataList((prev: any) => [...prev.slice(0, lastChildPosition + 1), newEntry, ...prev.slice(lastChildPosition + 1)]);
  }

  // Function to extract only required data for API
  function extractFormDataForAPI(data: any[], tab: string) {
    return data.map((item) => {
      const extractedData: any = {
        target_amount: item.target_amount,
        month: item.month,
        year: item.year,
        period_type: item.period_type,
      };

      // Add agent_id or team_id based on tab
      if (tab === 'individual') {
        extractedData.agent_id = item.agent_id;
      } else if (tab === 'sales-team') {
        extractedData.team_id = item.team_id;
      }

      return extractedData;
    });
  }

  function getGroupedEntries(formDataList: any[]) {
    const groupedEntries: Array<Array<{ entry: any; cardIdx: number }>> = [];
    let currentGroup: Array<{ entry: any; cardIdx: number }> = [];

    formDataList.forEach((entry, cardIdx) => {
      if (!entry.isTargetSet) {
        if (currentGroup.length > 0) {
          groupedEntries.push(currentGroup);
        }
        currentGroup = [{ entry, cardIdx }];
      } else {
        currentGroup.push({ entry, cardIdx });
      }
    });

    if (currentGroup.length > 0) {
      groupedEntries.push(currentGroup);
    }

    return groupedEntries;
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.sales_target.store);
    setErrors({});

    const apiData = extractFormDataForAPI(formDataList, activetab);
    setIsFormProcessing(true);
    try {
      const responseData = await createSalesTarget(apiData, activetab);

      // Handle 417 validation errors (index-wise format)
      if (responseData.status_code === 417) {
        if (handle417IndexWiseErrors(responseData, form.sales_target.store, tBe, setErrors, () => getGroupedEntries(formDataList))) {
          return;
        }
      }

      if (responseData.is_success) {
        setFormVers((prev) => prev + 1);
        setFormDataList([{ ...initFormData }]);
        activetab === 'individual' ? setAgentTableVers((prevTableVers) => prevTableVers + 1) : setTeamTableVers((prevTableVers) => prevTableVers + 1);
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    } finally {
      setIsFormProcessing(false);
    }
  }

  return (
    <div>
      <div className="panel">
        <form onSubmit={onSubmit} id={`${form.sales_target.store}`} key={formVers}>
          <div>
            {activetab === 'individual' && (
              <>
                {' '}
                <Label htmlFor="search" label={t('search')} isRequired />
                <FreeTextSearchInput
                  onChange={(data) => {
                    setKeywords(data);
                  }}
                />
              </>
            )}
          </div>
          <div className="row align-items-end">
            {(() => {
              const groupedEntries: Array<Array<{ entry: any; cardIdx: number }>> = [];
              let currentGroup: Array<{ entry: any; cardIdx: number }> = [];

              formDataList.forEach((entry, cardIdx) => {
                if (!entry.isTargetSet) {
                  // If we have a previous group, add it
                  if (currentGroup.length > 0) {
                    groupedEntries.push(currentGroup);
                  }
                  // Start new group with this parent
                  currentGroup = [{ entry, cardIdx }];
                } else {
                  // Add target set to current group
                  currentGroup.push({ entry, cardIdx });
                }
              });

              // Add the last group
              if (currentGroup.length > 0) {
                groupedEntries.push(currentGroup);
              }

              return groupedEntries.map((group, groupIdx) => (
                <div key={groupIdx} className="col-12 mb-4">
                  <div className="card">
                    <div className="card-body">
                      {(() => {
                        const groupedEntries: Array<Array<{ entry: any; cardIdx: number }>> = [];
                        let currentGroup: Array<{ entry: any; cardIdx: number }> = [];

                        formDataList.forEach((entry, cardIdx) => {
                          if (!entry.isTargetSet) {
                            if (currentGroup.length > 0) {
                              groupedEntries.push(currentGroup);
                            }
                            currentGroup = [{ entry, cardIdx }];
                          } else {
                            currentGroup.push({ entry, cardIdx });
                          }
                        });

                        if (currentGroup.length > 0) {
                          groupedEntries.push(currentGroup);
                        }

                        return (
                          groupedEntries.length > 1 && (
                            <div className="d-flex justify-content-end mb-3">
                              <Button color="danger" size="sm" onClick={() => removeEntireGroup(groupIdx)}>
                                <Flexicon icon="trash-02" variant="line" size={12} />
                              </Button>
                            </div>
                          )
                        );
                      })()}
                      <div className="row align-items-end">
                        {group.map(({ entry, cardIdx }) => (
                          <div key={cardIdx} className="col-12 mb-4">
                            <div className="row">
                              {(() => {
                                // Count total children for this entire group
                                const groupChildren = formDataList.filter((item) => item.isTargetSet && item.parentIndex === group[0].cardIdx);
                                const hasCloseButton = groupChildren.length >= 1;

                                return (
                                  <div className={hasCloseButton ? 'col-11' : 'col-12'}>
                                    <div className="row">
                                      {(cardIdx === 0 || entry.isNewColumn) && activetab === 'individual' && (
                                        <div className="col-12 col-md-6 col-lg-3 mb-3 custom-select">
                                          <Label label={t('sales_agent')} isRequired />
                                          <AsyncSelect
                                            multiple
                                            onChange={(value) => handleFormChange(cardIdx, 'agent_id', value)}
                                            className={`form-control error-agent_id_${cardIdx}`}
                                            loadOptions={(searchValue, currentPage) => fetchAllAgentData(searchValue, currentPage, keywords)}
                                            option={{
                                              value: 'id',
                                              label: 'display_name',
                                            }}
                                          />
                                        </div>
                                      )}
                                      {(cardIdx === 0 || entry.isNewColumn) && activetab === 'sales-team' && (
                                        <div className="col-12 col-md-6 col-lg-3 mb-3 custom-select">
                                          <Label htmlFor="search" label={t('sales_team')} isRequired />
                                          <AsyncSelect
                                            multiple
                                            onChange={(value) => handleFormChange(cardIdx, 'team_id', value)}
                                            className={`form-control error-team_id_${cardIdx}`}
                                            loadOptions={fetchAllSalesTeamData}
                                            option={{
                                              value: 'id',
                                              label: 'name',
                                            }}
                                          />
                                        </div>
                                      )}
                                      {entry.isTargetSet && <div className="col-12 col-md-6 col-lg-3 mb-3"></div>}
                                      <div className="col-12 col-md-6 col-lg-3 mb-3">
                                        <Label htmlFor="Target Period" label={t('target_period')} isRequired />
                                        <Select
                                          onChange={(_, data) => {
                                            handleFormChange(cardIdx, 'period_type', data.value);
                                            const currentYear = new Date().getFullYear();
                                            if (data.value === 'monthly') {
                                              handleFormChange(cardIdx, 'month', new Date().getMonth() + 1);
                                              handleFormChange(cardIdx, 'year', currentYear.toString());
                                              setPeriodVers((prev) => prev + 1);
                                            } else {
                                              handleFormChange(cardIdx, 'month', null);
                                              handleFormChange(cardIdx, 'year', currentYear.toString());
                                              setPeriodVers((prev) => prev + 1);
                                            }
                                          }}
                                          options={[
                                            { label: t('monthly'), value: 'monthly' },
                                            { label: t('yearly'), value: 'yearly' },
                                          ]}
                                          option={{ label: 'label', value: 'value' }}
                                          defaultValue={{ label: entry.period_type, value: entry.period_type }}
                                        />
                                      </div>
                                      <div key={`${cardIdx}-${entry.period_type}-${periodVers}`} className="col-12 col-md-6 col-lg-3 mb-3">
                                        {entry.period_type === 'monthly' ? (
                                          <div>
                                            <Label label={t('select_month')} isRequired />
                                            <Select
                                              onChange={(value) => handleFormChange(cardIdx, 'month', value)}
                                              options={months}
                                              option={{ label: 'label', value: 'value' }}
                                              isSearchable={true}
                                              defaultValue={months.find((m) => m.value === entry.month)}
                                            />
                                          </div>
                                        ) : (
                                          <div>
                                            <Label label={t('select_year')} isRequired />
                                            <Select
                                              onChange={(value) => handleFormChange(cardIdx, 'year', value)}
                                              options={years}
                                              option={{ label: 'label', value: 'value' }}
                                              isSearchable={true}
                                              defaultValue={years.find((y) => y.value === Number(entry.year))}
                                            />
                                          </div>
                                        )}
                                      </div>
                                      <div className="col-12 col-md-6 col-lg-3 mb-3">
                                        <Label label={t('target_amount')} isRequired />
                                        <Input
                                          value={entry.target_amount}
                                          onChange={(e) => handleFormChange(cardIdx, 'target_amount', e.target.value)}
                                          id={`target_amount_${cardIdx}`}
                                          className={`form-control error-target_amount_${cardIdx}`}
                                          name={`target_amount_${cardIdx}`}
                                          type="number"
                                          min={0}
                                        />
                                      </div>
                                    </div>
                                  </div>
                                );
                              })()}
                              {(() => {
                                // Count total children for this entire group
                                const groupChildren = formDataList.filter((item) => item.isTargetSet && item.parentIndex === group[0].cardIdx);

                                return (
                                  groupChildren.length >= 1 && (
                                    <div className="col-1 d-flex justify-content-center align-items-center">
                                      <Button color="danger" size="sm" onClick={() => removeColumn(cardIdx)}>
                                        <Flexicon icon="x-close" variant="line" size={12} />
                                      </Button>
                                    </div>
                                  )
                                );
                              })()}
                            </div>
                            {errors[cardIdx] && errors[cardIdx].length > 0 && (
                              <div className="err-msg mt-2">
                                {errors[cardIdx].map((_, i) => (
                                  <div key={i}>{t('already_exists')}</div>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                        {!group[0].entry.isTargetSet && (
                          <div className="mt-2 d-flex justify-content-end">
                            <div onClick={() => addTargetSet(group[0].cardIdx)} className="d-flex gap-2 align-items-center text-primary pointer">
                              <Flexicon icon="plus" variant="line" size={14} />
                              {t('add')}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ));
            })()}
          </div>
          <div className="d-flex justify-content-end">
            <div onClick={() => addNewColumn()} className="d-flex gap-2 align-items-center text-primary pointer">
              <Flexicon icon="plus" variant="line" size={14} />
              {t('add_target_set')}
            </div>
          </div>
          <div className="d-flex justify-content-end gap-2 mt-5">
            <Button
              text={t('cancel')}
              color="light"
              width="sm"
              onClick={() => {
                setCurrentPg('first');
              }}
            />
            <Button className="d-flex align-items-center gap-1" type="submit" isLoading={isFormProcessing}>
              <Flexicon icon="save-01" variant="line" size={18} />
              <span>{t('set_target')}</span>
            </Button>
          </div>
        </form>
      </div>
      <div>
        <div className="panel">
          <div className="panel-title">{t('previous_target_history')}</div>
          <div className="card-body">
            <SalesTargetList teamTableVers={teamTableVers} agentTableVers={agentTableVers} activetab={activetab} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default SalesTargetCreateContent;
