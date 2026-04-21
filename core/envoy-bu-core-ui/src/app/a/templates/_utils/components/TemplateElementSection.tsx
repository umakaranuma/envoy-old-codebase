import { Input, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { IFormElementGroup } from '../model';
import IconBtn from './IconBtn';
import { TemplateSVG } from './TemplateSVG';
import { getAllTemplateFormElements } from '../api-service';
import ElementCreate from './ElementCreate';
import { useParams } from 'next/navigation';

function TemplateElementSection({
  activeStepId,
  selectedPanelId,
  setElements,
  groupElement,
  setgroupElement,
}: {
  activeStepId: number | null;
  selectedPanelId: number | null;
  setElements: any;
  groupElement: any;
  setgroupElement: any;
}) {
  const params = useParams();
  const templateId = params.id?.toString() || '';
  const [loading, setLoading] = useState(true);
  const [error, seterror] = useState('');
  const [data, setData] = useState<IFormElementGroup[]>();
  const [searchElementString, setSearchElementString] = useState('');
  const [createElementVisible, setCreateElementVisible] = useState(false);
  const [selectedElementId, setSelectedElementId] = useState(0);
  const [selectedElementCode, setSelectedElementCode] = useState('');
  const [selectedElementCategory, setSelectedElementCategory] = useState('');
  const [createFormKey, setCreateFormKey] = useState(0);

  const fetchTemplateFormElementsData = async (searchValue: string) => {
    try {
      setLoading(true);
      const response = await getAllTemplateFormElements(
        {
          search: searchValue.toLowerCase(),
        },
        true,
      );

      if (response.is_success) {
        setData(response.result.elements || []);
        setgroupElement(response.result.group_elements || []);
      }
    } catch (error: any) {
      console.error('Error fetching template form elements:', error);
      seterror(error);
    } finally {
      setLoading(false);
    }
  };

  const handleElementClick = (id: number) => {
    setCreateElementVisible(true);
    setSelectedElementId(id);
  };
  const handleCreateFormOnCancel = () => {
    setCreateElementVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setCreateElementVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  useEffect(() => {
    fetchTemplateFormElementsData(searchElementString);
  }, [searchElementString]);

  return (
    <div className="col-12 col-md-3 col-lg-3 mb-3 overflow-scroll hide-scrollbar template-view">
      <Input
        type="search"
        id="input-search"
        placeholder="Search...."
        size="sm"
        onChange={(e: any) => {
          setSearchElementString(e.target.value);
        }}
      />

      {loading ? (
        <div className="text-center">
          <TemplateViewSkeleton />
        </div>
      ) : error ? (
        <div className="p-3 d-flex justify-content-center align-items-center text-danger">Failed to load elements. Please try again.</div>
      ) : data?.length === 0 ? (
        <div className="p-3 d-flex justify-content-center align-items-center text-muted">No elements found</div>
      ) : (
        data?.map((group) => (
          <div key={group.group} className="custom-card mt-3">
            <div className="panel-title">{group.group}</div>
            <div className="container">
              <div className="d-flex align-items-center flex-wrap gap-2">
                {group.elements.map((element: any) => (
                  <IconBtn
                    key={element.id}
                    icon={<TemplateSVG icon={element.code} width={22} height={22} />}
                    title={element.title}
                    onClick={() => {
                      handleElementClick(element.id);
                      setSelectedElementCode(element.code);
                      setSelectedElementCategory(element.category);
                    }}
                  />
                ))}
              </div>
            </div>
          </div>
        ))
      )}
      <ElementCreate
        selectedElementCode={selectedElementCode}
        selectedPanelId={selectedPanelId}
        activeStepId={activeStepId}
        key={createFormKey}
        templateId={templateId}
        isOpen={createElementVisible}
        onCancel={handleCreateFormOnCancel}
        afterSave={handleAfterSave}
        selectedElementId={selectedElementId}
        groupElement={groupElement}
        setElements={setElements}
        selectedElementCategory={selectedElementCategory}
      />
    </div>
  );
}

export default TemplateElementSection;

const TemplateViewSkeleton = () => {
  return (
    <>
      {[...Array(3)].map((_, i) => (
        <div key={i} className="row mt-3">
          <Skeleton height="25px" />
          <div className="d-flex flex-wrap gap-2 mt-3">
            {[...Array(6)].map((_, j) => (
              <Skeleton key={j} height="45px" width="60px" />
            ))}
          </div>
        </div>
      ))}
    </>
  );
};
