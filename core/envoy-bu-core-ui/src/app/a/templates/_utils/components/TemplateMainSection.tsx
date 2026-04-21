import React from 'react';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { EditableText } from './EditableText';
import StepSection from './StepSection';
import ElementSection from './ElementSection';
import PannelOption from './PannelOption';
import { Flexicon } from '@apptimus-ui/flexicon';
import { IStep, IPanel, IElement } from '../model';
import { useTrans } from '@/helpers/services/lang/langService';

interface TemplateMainProps {
  loading: boolean;
  updateTemplateHeading: boolean;
  template: any;
  handleEditTemplate: (templateId: string, newTitle: string) => void;
  handleEditPanel: (templateId: string, panelId: any, newTitle: string) => void;
  templateId: string;
  activeStepId: number | null;
  setActiveStepId: (id: number) => void;
  steps: IStep[];
  setSteps: React.Dispatch<React.SetStateAction<IStep[]>>;
  panels: IPanel[];
  setPanels: React.Dispatch<React.SetStateAction<IPanel[]>>;
  selectedPanelId: number;
  setSelectedPanelId: (id: number) => void;
  SetDeleteModel: (open: boolean) => void;
  handleCreatePanel: (templateId: string) => void;
  creatLoading: boolean;
  elements: IElement[];
  setElements: React.Dispatch<React.SetStateAction<IElement[]>>;
  setSelectedElementId: any;
  selectedElementId: number | null;
  updatePanelHeading: boolean;
  setIsPreviewOpen: (open: boolean) => void;
  isPreviewOpen: boolean;
  groupElement: any[];
}

const TemplateMainSection: React.FC<TemplateMainProps> = ({
  loading,
  updateTemplateHeading,
  template,
  handleEditTemplate,
  handleEditPanel,
  templateId,
  activeStepId,
  setActiveStepId,
  steps,
  setSteps,
  panels,
  setPanels,
  selectedPanelId,
  setSelectedPanelId,
  SetDeleteModel,
  handleCreatePanel,
  creatLoading,
  elements,
  setElements,
  setSelectedElementId,
  selectedElementId,
  updatePanelHeading,
  setIsPreviewOpen,
  isPreviewOpen,
}) => {
  const t = useTrans('label.template,otr.common');
  return (
    <div className={`col-12 col-md-9 col-lg-9 template-view ${isPreviewOpen ? 'w-100' : 'overflow-y-scroll'}`}>
      <div className="bg-white custom-card py-2 px-2 rounded-3 mb-3">
        <div>
          {loading ? (
            <div className="d-flex justify-content-center">
              <Skeleton height="30px" width="250px" />
            </div>
          ) : !updateTemplateHeading ? (
            <div>
              {!isPreviewOpen && (
                <div className="d-flex justify-content-end">
                  <Button color="light" className="p-2" onClick={() => setIsPreviewOpen(!isPreviewOpen)}>
                    <Flexicon icon="maximize-02" variant="line" className="text-primary" size={18} />
                  </Button>
                </div>
              )}
              <div className="text-center fw-semibold fs-18 mb-3">
                <EditableText
                  title={template?.name || 'Untitled Template'}
                  onChange={(newTitle, _) => {
                    handleEditTemplate(templateId, newTitle);
                  }}
                />
              </div>
            </div>
          ) : (
            <div className="d-flex justify-content-center">
              <Skeleton height="30px" width="250px" />
            </div>
          )}
        </div>
        {/* Step Section */}
        <StepSection activeStepId={activeStepId} loading={loading} setActiveStepId={setActiveStepId} steps={steps} setSteps={setSteps} setPanels={setPanels} />
      </div>

      {loading ? (
        <div className="d-flex flex-column gap-3">
          {[1, 2, 3].map((_, index) => (
            <div key={index} className="bg-white custom-card p-4 rounded-3">
              <Skeleton height="30px" width="200px" className="mb-3" />
              <div className="row">
                <div className="col-12 mb-3">
                  <Skeleton height="50px" />
                </div>
                <div className="col-md-6 mb-3">
                  <Skeleton height="50px" />
                </div>
                <div className="col-md-6 mb-3">
                  <Skeleton height="50px" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div>
          {panels
            .filter((panel) => panel.step_id === activeStepId)
            .map((panel) => (
              <div key={panel.id} className="mb-3">
                <div className="gap-1 d-flex w-100">
                  <div
                    className={`pointer custom-card bg-white p-2 px-3 pt-3 rounded-3 w-100 shadow-sm ${selectedPanelId === panel.id ? 'border border-primary border-2' : ''}`}
                    onClick={() => setSelectedPanelId(panel.id)}
                  >
                    {!updatePanelHeading ? (
                      <div className="fw-semibold">
                        <EditableText
                          id={panel.id}
                          title={panel.title || 'Untitled Panel'}
                          onChange={(newTitle, id) => {
                            handleEditPanel(templateId, id, newTitle);
                          }}
                        />
                      </div>
                    ) : (
                      <Skeleton height="50px" />
                    )}

                    {/* element Container */}
                    <div className="my-2">
                      <ElementSection
                        elements={elements}
                        setElements={setElements}
                        setSelectedElementId={setSelectedElementId}
                        selectedElementId={selectedElementId}
                        pannelId={panel.id}
                        templateId={templateId}
                      />
                    </div>
                  </div>

                  {/* Panel Options - Right Side */}
                  {selectedPanelId === panel.id && !isPreviewOpen && (
                    <div className="template-panel-options">
                      <div className="h-100" onClick={(e) => e.stopPropagation()}>
                        <PannelOption setDeleteModel={SetDeleteModel} panelId={selectedPanelId} templateId={templateId} setPanels={setPanels} setElements={setElements} />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

          {/* Add Panel Button */}
          <Button
            className="w-100 text-white"
            onClick={(e) => {
              e.preventDefault();
              handleCreatePanel(templateId);
            }}
            type="button"
            isLoading={creatLoading}
          >
            {t('add_panel')}
          </Button>

          {steps.length > 0 && (
            <div className="d-flex justify-content-end gap-3 mt-3">
              <Button
                onClick={() => {
                  const currentIndex = steps.findIndex((step) => step.id === activeStepId);
                  if (currentIndex > 0) {
                    setActiveStepId(steps[currentIndex - 1].id);
                  }
                }}
                disabled={steps.findIndex((step) => step.id === activeStepId) === 0}
              >
                <Flexicon icon="chevron-left" variant="line" />
                {t('previous')}
              </Button>

              <Button
                onClick={() => {
                  const currentIndex = steps.findIndex((step) => step.id === activeStepId);
                  if (currentIndex < steps.length - 1) {
                    setActiveStepId(steps[currentIndex + 1].id);
                  }
                }}
                disabled={steps.findIndex((step) => step.id === activeStepId) === steps.length - 1}
              >
                {t('next')} <Flexicon icon="chevron-right" variant="line" />
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TemplateMainSection;
