import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import ElementType from '@/components/others/common/form/ElementType';
import { IFormTemplate, IElement, Step } from '@/components/others/common/form/template-modal';
import { getRiskRegisterFormTemplate } from '../../api-service';
import FormStepper from '@/components/others/common/form/FormStepper';
import Link from 'next/link';

function RiskRegisterCreateForm({
  riskId,
  onBack,
  isFormProcessing,
  onSubmit,
  currentPath,
  riskTypeId,
}: {
  riskId: string;
  onBack: Function;
  isFormProcessing: boolean;
  onSubmit: Function;
  currentPath: string;
  riskTypeId: string;
}) {
  const t = useTrans('label.claim,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const router = useRouter();
  const [currentTab, setCurrentTab] = useState({} as Step);
  const [currentTabIndex, setCurrentTabIndex] = useState(0);
  const [formData, setFormData] = useState([] as IElement[]);
  const [templateData, setTemplateData] = useState<IFormTemplate>({} as IFormTemplate);
  const [skeleton, setSkeleton] = useState(false);

  const fetchTemplateData = async () => {
    if (riskId) {
      const responseData = await getRiskRegisterFormTemplate(riskId);
      if (responseData?.is_success) {
        setTemplateData(responseData.result);
        setFormData(responseData.result.elements);
        const templateResponseData = responseData.result as IFormTemplate;
        if (templateResponseData.steps && templateResponseData.steps.length > 0) {
          const defaultTabSlug = templateResponseData.steps[0].title.toLowerCase().replace(/\s+/g, '_');
          const foundIndex = templateResponseData.steps.findIndex((step) => step.title.toLowerCase().replace(/\s+/g, '_') === defaultTabSlug);

          if (foundIndex !== -1) {
            const step = templateResponseData.steps[foundIndex];
            setCurrentTab(step);
            setCurrentTabIndex(foundIndex);
          }
        }
        setSkeleton(false);
      } else {
        setFormData([] as IElement[]);
        setSkeleton(false);
      }
    }
  };

  useEffect(() => {
    if (riskId) {
      setSkeleton(true);
      fetchTemplateData();
      router.push(`${currentPath}`);
    }
  }, [riskId]);

  const onFormChange = (elementId: number, value: any) => {
    setFormData((prevFormData) => prevFormData.map((item) => (item.id === elementId ? { ...item, value } : item)));
  };

  const handleValidation = () => {
    clearError(form.claim.store);
    const error: { [key: string]: Array<{ error_type: string; tokens: { _attribute: string } }> } = {};

    if (templateData.template.type === 'multi_step_form') {
      const currentStep = templateData.steps[currentTabIndex];
      const currentStepElements = formData.filter((element) => element.step_id === currentStep.id);
      currentStepElements.forEach((element) => {
        if (element.is_required && !element.value) {
          error[element.id] = [
            {
              error_type: 'required',
              tokens: {
                _attribute: element.id.toString(),
              },
            },
          ];
        }
      });
    } else {
      formData.forEach((element) => {
        if (element.is_required && !element.value) {
          error[element.id] = [
            {
              error_type: 'required',
              tokens: {
                _attribute: element.id.toString(),
              },
            },
          ];
        }
      });
    }
    console.log('error', Object.keys(error));
    console.log('formData', formData);
    if (Object.keys(error).length > 0) {
      printError(error, form.claim.store, tBe);
    } else {
      if (templateData.template.type === 'multi_step_form') {
        if (currentTabIndex === templateData.steps.length - 1) {
          onSubmit(formData);
        } else {
          const nextIndex = currentTabIndex + 1;
          const nextStep = templateData.steps[nextIndex];
          setCurrentTab(nextStep);
          setCurrentTabIndex(nextIndex);
        }
      } else {
        onSubmit(formData);
      }
    }
  };

  return (
    <>
      {skeleton ? (
        <Skeleton className="w-100" height={'400px'} />
      ) : (
        <div>
          {formData.length > 0 ? (
            <>
              <>{templateData.steps && templateData.steps.length > 0 && <FormStepper templateName={templateData.template.name} steps={templateData.steps} currentTabId={currentTab.id} />}</>
              <>
                {templateData.panels &&
                  templateData.panels.length > 0 &&
                  templateData.panels.map((panel, index) => (
                    <div key={panel.id} className={templateData.template?.type === 'multi_step_form' ? `d-${currentTab.id && currentTab.id === panel.step_id ? 'block' : 'none'}` : 'd-block'}>
                      <div className="card-body bg-white p-3 rounded-3 mb-3" key={index}>
                        <div className="panel-title">{panel.title}</div>
                        {
                          <div className="row">
                            {formData
                              .filter((element) => element.panel_id === panel.id)
                              .map((element, index) => (
                                <div id={`${form.claim.store}`} key={index} className={`col-12 col-md-${element.column_size} mb-3`}>
                                  <ElementType
                                    type={element.code}
                                    onChange={(value) => {
                                      onFormChange(element.id, value);
                                      console.log('value' + value);
                                      console.log('element.id' + element.id);
                                    }}
                                    options={element.options}
                                    isRequired={element.is_required !== 0}
                                    label={element.label}
                                    value={element.value}
                                    elementId={element.id.toString()}
                                  />
                                </div>
                              ))}
                          </div>
                        }
                      </div>
                    </div>
                  ))}
              </>
              {(templateData.template && templateData.template.type) === 'multi_step_form' ? (
                <div className="d-flex justify-content-start gap-2 mt-3">
                  <Button
                    color="light"
                    className="d-flex align-items-center gap-1"
                    onClick={() => {
                      if (currentTabIndex > 0) {
                        const prevIndex = currentTabIndex - 1;
                        const prevStep = templateData.steps[prevIndex];
                        setCurrentTab(prevStep);
                        setCurrentTabIndex(prevIndex);
                      } else {
                        onBack();
                      }
                    }}
                  >
                    <Flexicon icon="chevron-left" variant="line" size={18} />
                    <span className="d-none d-sm-inline">{t('back')}</span>
                  </Button>

                  {currentTabIndex < templateData.steps.length - 1 ? (
                    <Button
                      color="primary"
                      className="d-flex align-items-center gap-1"
                      onClick={() => {
                        handleValidation();
                      }}
                    >
                      <span className="d-none d-sm-inline">{t('next')}</span>
                      <Flexicon icon="chevron-right" variant="line" size={18} />
                    </Button>
                  ) : (
                    <Button color="primary" onClick={handleValidation} text={t('save')} isLoading={isFormProcessing} />
                  )}
                </div>
              ) : (
                <div className="d-flex justify-content-start gap-2 mt-3">
                  <Button color="light" className="d-flex align-items-center gap-1" onClick={() => onBack()}>
                    <Flexicon icon="chevron-left" variant="line" size={18} />
                    <span className="d-none d-sm-inline">{t('back')}</span>
                  </Button>
                  <Button color="primary" onClick={handleValidation} text={t('save')} isLoading={isFormProcessing} />
                </div>
              )}
            </>
          ) : (
            <div className="text-center p-5 card">
              <div className="text-muted fs-15 fw-semibold my-2">{t('no_form_config')}</div>
              <Link className="text-primary clickable-text fs-14" href={`/a/product-categories/${riskTypeId}?t=forms`}>
                {t('configure_it_now')}
              </Link>
            </div>
          )}
        </div>
      )}
    </>
  );
}

export default RiskRegisterCreateForm;
