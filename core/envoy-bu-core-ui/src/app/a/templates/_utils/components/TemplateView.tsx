'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { IElement, IPanel, IStep, ITemplate } from '../model';
import TemplateElementSection from './TemplateElementSection';
import { createPanel, getOneTemplate, UpdatePanel, updateTemplate } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import PanelDelete from './PanelDelete';
import TemplateMainSection from './TemplateMainSection';
import { Modal, ModalBody } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import GoBack from '@/components/others/page-related/GoBack';
import { useTrans } from '@/helpers/services/lang/langService';

export const TemplateView = () => {
  const t = useTrans('label.template,otr.common');
  const params = useParams();
  const templateId = params.id?.toString() || '';
  const [loading, setLoading] = useState(true);
  const [creatLoading, setCreateLoading] = useState(false);
  const [error, setError] = useState('');
  const [template, setTemplate] = useState<ITemplate>();
  const [steps, setSteps] = useState<IStep[]>([]);
  const [panels, setPanels] = useState<IPanel[]>([]);
  const [elements, setElements] = useState<IElement[]>([]);
  const [selectedPanelId, setSelectedPanelId] = useState<number>(0);
  const [selectedElementId, setSelectedElementId] = useState<number | null>(null);
  const [activeStepId, setActiveStepId] = useState<number | null>(null);
  const [deleteModel, SetDeleteModel] = useState(false);
  const [updatePanelHeading, setUpdatePanelHeading] = useState(false);
  const [updateTemplateHeading, setUpdateTemplateHeading] = useState(false);
  const [groupElement, setgroupElement] = useState<any[]>([]);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const router = useRouter();
  const fetchTemplateData = async (templateId: string) => {
    try {
      setLoading(true);
      const response = await getOneTemplate(templateId);

      if (response.is_success) {
        setTemplate(response.result?.template);
        setSteps(response.result?.steps || []);
        setPanels(response.result?.panels || []);
        setElements(response.result?.elements || []);

        // Set the first step as active by default
        if (response.result?.steps?.length) {
          setActiveStepId(response.result.steps[0].id);
        }
      } else {
        setError(response.message || 'Failed to fetch template');
      }
    } catch (error: any) {
      console.error('Error fetching template form elements:', error);
      setError(error.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePanel = async (templateId: string) => {
    try {
      setCreateLoading(true);
      const response = await createPanel({ step_id: activeStepId }, templateId);

      if (response.is_success && response.result) {
        setPanels((prevPanels) => [...prevPanels, response.result]);
        toaster.success('Panel created successfully!');
      } else {
        const errorMsg = response.message || 'Failed to create panel';
        toaster.error(errorMsg);
        setError(errorMsg);
      }
    } catch (error: any) {
      console.error('Panel creation failed:', error);
      toaster.error(error.message || 'An unexpected error occurred');
      setError(error.message);
    } finally {
      setCreateLoading(false);
    }
  };

  const handleEditPanel = async (templateId: string, pannelId: any, newTitle: any) => {
    try {
      setUpdatePanelHeading(true);

      const response = await UpdatePanel({ title: newTitle, step_id: activeStepId }, templateId, pannelId);
      if (response.is_success && response.result) {
        setPanels(panels.map((p) => (p.id === pannelId ? { ...p, title: newTitle } : p)));
        toaster.success('Panel Updated successfully!');
      } else {
        const errorMsg = response.message || 'Failed to create panel';
        toaster.error(errorMsg);
        setError(errorMsg);
      }
    } catch (error: any) {
      console.error('Panel updated failed:', error);
      toaster.error(error.message || 'An unexpected error occurred');
      setError(error.message);
    } finally {
      setUpdatePanelHeading(false);
    }
  };

  const handleEditTemplate = async (templateId: string, newTitle: any) => {
    try {
      setUpdateTemplateHeading(true);

      const response = await updateTemplate({ title: newTitle, type: template?.type, description: template?.description }, templateId);
      if (response.is_success && response.result) {
        setTemplate({
          ...template,
          name: newTitle,
        } as ITemplate);

        toaster.success('Template Name Updated successfully!');
      } else {
        const errorMsg = response.message || 'Failed to create panel';
        toaster.error(errorMsg);
        setError(errorMsg);
      }
    } catch (error: any) {
      console.error('Template Name updated failed:', error);
      toaster.error(error.message || 'An unexpected error occurred');
      setError(error.message);
    } finally {
      setUpdateTemplateHeading(false);
    }
  };

  useEffect(() => {
    fetchTemplateData(templateId);
    console.log(error);
  }, [templateId]);

  useEffect(() => {
    // If steps array is empty, try to select first panel (if panels exist)
    if (steps.length === 0 && panels.length > 0) {
      setSelectedPanelId(panels[0].id);
      return;
    }

    // Normal case - when we have steps
    if (activeStepId && panels.length > 0) {
      // Find panels belonging to the active step
      const stepPanels = panels.filter((panel) => panel.step_id === activeStepId);

      // If there are panels for this step, select the first one
      if (stepPanels.length > 0) {
        setSelectedPanelId(stepPanels[0].id);
      } else {
        // No panels for this step - set to null
        setSelectedPanelId(0);
      }
    } else {
      // No active step or no panels - set to null
      setSelectedPanelId(0);
    }
  }, [activeStepId, panels, steps.length]);

  return (
    <>
      {/* <style>{`
      @media (min-width: 768px) {
        body { 
          max-height: calc(100vh); 
          overflow-y: hidden;
        }
      }
    `}</style> */}
      <GoBack goTo={() => router.push('/a/templates')} title={t('templates')} skeleton={false} />
      <div className="panel">
        <div className="row mt-3">
          {/* Left Column */}
          <TemplateElementSection activeStepId={activeStepId} selectedPanelId={selectedPanelId} setElements={setElements} groupElement={groupElement} setgroupElement={setgroupElement} />

          {/* Right Column */}
          <TemplateMainSection
            loading={loading}
            updateTemplateHeading={updateTemplateHeading}
            template={template}
            handleEditTemplate={handleEditTemplate}
            handleEditPanel={handleEditPanel}
            templateId={templateId}
            activeStepId={activeStepId}
            setActiveStepId={setActiveStepId}
            steps={steps}
            setSteps={setSteps}
            panels={panels}
            setPanels={setPanels}
            selectedPanelId={selectedPanelId}
            setSelectedPanelId={setSelectedPanelId}
            SetDeleteModel={SetDeleteModel}
            handleCreatePanel={handleCreatePanel}
            creatLoading={creatLoading}
            elements={elements}
            setElements={setElements}
            setSelectedElementId={setSelectedElementId}
            selectedElementId={selectedElementId}
            updatePanelHeading={updatePanelHeading}
            setIsPreviewOpen={setIsPreviewOpen}
            isPreviewOpen={isPreviewOpen}
            groupElement={groupElement}
          />
        </div>
      </div>
      {deleteModel && (
        <PanelDelete
          selectedPanelId={selectedPanelId}
          templateId={templateId}
          isOpen={deleteModel}
          onCancel={() => {
            SetDeleteModel(false);
          }}
          afterDelete={() => {
            SetDeleteModel(false);
            setPanels(panels.filter((panel) => panel.id !== selectedPanelId));
          }}
        />
      )}

      {/* Preview Model */}

      {isPreviewOpen && (
        <Modal isOpen={isPreviewOpen} size="fullscreen">
          <div className=" d-flex justify-content-end p-3">
            <Button color="light" className="p-2" onClick={() => setIsPreviewOpen(!isPreviewOpen)}>
              <Flexicon icon="maximize-02" variant="line" className="text-primary" size={20} />
            </Button>
          </div>
          <ModalBody>
            <TemplateMainSection
              loading={loading}
              updateTemplateHeading={updateTemplateHeading}
              template={template}
              handleEditTemplate={handleEditTemplate}
              handleEditPanel={handleEditPanel}
              templateId={templateId}
              activeStepId={activeStepId}
              setActiveStepId={setActiveStepId}
              steps={steps}
              setSteps={setSteps}
              panels={panels}
              setPanels={setPanels}
              selectedPanelId={selectedPanelId}
              setSelectedPanelId={setSelectedPanelId}
              SetDeleteModel={SetDeleteModel}
              handleCreatePanel={handleCreatePanel}
              creatLoading={creatLoading}
              elements={elements}
              setElements={setElements}
              setSelectedElementId={setSelectedElementId}
              selectedElementId={selectedElementId}
              updatePanelHeading={updatePanelHeading}
              setIsPreviewOpen={setIsPreviewOpen}
              isPreviewOpen={isPreviewOpen}
              groupElement={groupElement}
            />
          </ModalBody>
        </Modal>
      )}
    </>
  );
};
