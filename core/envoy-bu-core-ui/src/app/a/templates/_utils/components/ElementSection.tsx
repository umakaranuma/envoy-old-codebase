import React, { useState } from 'react';
import { IElement } from '../model';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import ElementType from './ElementType';
import ElementDelete from './ElementDelete';
import ElementEdit from './ElementEdit';

interface ElementSectionProps {
  elements: IElement[];
  setElements: React.Dispatch<React.SetStateAction<IElement[]>>;
  setSelectedElementId: React.Dispatch<React.SetStateAction<number | null>>;
  selectedElementId: number | null;
  pannelId: number;
  templateId: string;
  groupElement?: any[];
}

function getGroupLabels(element: IElement, groupElement: any[]): string[] {
  if (element.category === 'input_group') {
    const labels = (Array.isArray(groupElement) ? groupElement : []).filter((group: any) => group.group_id === element.id).map((group: any) => group.title);
    return labels;
  }
  return [];
}

// Recursive render function
function renderElement(
  element: IElement,
  allElements: IElement[],
  groupElement: any[] | undefined,
  handlers: {
    setSelectedElementId: React.Dispatch<React.SetStateAction<number | null>>;
    setSelectedElementIdForEdit: React.Dispatch<React.SetStateAction<string>>;
    setSelectedElementCode: React.Dispatch<React.SetStateAction<string>>;
    setEditModel: React.Dispatch<React.SetStateAction<boolean>>;
    setDeleteModel: React.Dispatch<React.SetStateAction<boolean>>;
    setSelectedElementCategory: React.Dispatch<React.SetStateAction<string>>;
    setSelectedElement: React.Dispatch<React.SetStateAction<any | null>>;
  },
  selectedElementId: number | null,
) {
  // Find children of this element
  const children = allElements.filter((child) => child.parent_id === element.id);

  // If this is a group child, force col-12 (full width)
  const isGroupChild = element.parent_id !== null;
  const colClass = isGroupChild ? 'col-12' : `col-12 col-md-${element.column_size || 6}`;

  return (
    <div
      key={element.id}
      className={`${colClass} p-1 position-relative rounded ${selectedElementId === element.id ? 'border border-primary' : ''}`}
      onClick={() => handlers.setSelectedElementId(element.id)}
    >
      <div className={`d-flex justify-content-end gap-2 ${selectedElementId === element.id ? '' : 'd-none'}`}>
        <Button
          color="info"
          size="sm"
          className="p-1"
          onClick={(e) => {
            e.stopPropagation();
            handlers.setSelectedElementIdForEdit(element.id.toString());
            handlers.setSelectedElementCode(element.code);
            handlers.setEditModel(true);
            handlers.setSelectedElementCategory(element.category);
            handlers.setSelectedElement(element);
          }}
        >
          <Flexicon icon="edit-05" variant="line" size={16} />
        </Button>
        <Button
          size="sm"
          color="danger"
          className="p-1"
          onClick={(e) => {
            e.stopPropagation();
            handlers.setSelectedElementIdForEdit(element.id.toString());
            handlers.setSelectedElementCode(element.code);
            handlers.setDeleteModel(true);
            handlers.setSelectedElementCategory(element.category);
          }}
        >
          <Flexicon icon="trash-03" variant="line" size={16} />
        </Button>
      </div>
      <ElementType type={element.code} isRequired={Boolean(element.is_required)} label={element.label} options={element.options} value={element.value} />
      {getGroupLabels(element, groupElement || []).length > 0}
      {/* Render children recursively, indented */}
      {children.length > 0 && <div className="">{children.map((child) => renderElement(child, allElements, groupElement, handlers, selectedElementId))}</div>}
    </div>
  );
}

function ElementSection({ elements, setElements, setSelectedElementId, selectedElementId, pannelId, templateId, groupElement }: ElementSectionProps) {
  const [deleteModel, setDeleteModel] = useState(false);
  const [editModel, setEditModel] = useState(false);
  const [selectedElementIdForEdit, setSelectedElementIdForEdit] = useState<string>('');
  const [selectedElementCode, setSelectedElementCode] = useState<string>('');
  const [selectedElementCategory, setSelectedElementCategory] = useState('');
  const [selectedElement, setSelectedElement] = useState<any | null>(null);

  const filteredElements = elements.filter((element: IElement) => {
    return element.panel_id === pannelId;
  });

  return (
    <>
      <div className="row">
        {filteredElements.length > 0 ? (
          filteredElements
            .filter((element) => element.parent_id === null)
            .map((element) =>
              renderElement(
                element,
                filteredElements,
                groupElement,
                {
                  setSelectedElementId,
                  setSelectedElementIdForEdit,
                  setSelectedElementCode,
                  setEditModel,
                  setDeleteModel,
                  setSelectedElementCategory,
                  setSelectedElement,
                },
                selectedElementId,
              ),
            )
        ) : (
          <div className="col-12 text-center p-4 m-4 text-muted">No elements found</div>
        )}
      </div>

      {deleteModel && (
        <ElementDelete
          elementId={selectedElementIdForEdit}
          isOpen={deleteModel}
          onCancel={() => {
            setSelectedElementIdForEdit('');
            setDeleteModel(false);
            setSelectedElement(null);
          }}
          afterDelete={() => {
            setDeleteModel(false);
            setSelectedElement(null);
            setElements(elements.filter((element) => element.id.toString() !== selectedElementIdForEdit));
          }}
          templateId={templateId}
          elements={filteredElements}
          selectedElementCategory={selectedElementCategory}
        />
      )}

      {editModel && (
        <ElementEdit
          setElements={setElements}
          selectedElementCode={selectedElementCode}
          editId={selectedElementIdForEdit}
          isOpen={editModel}
          onCancel={() => {
            setSelectedElementIdForEdit('');
            setEditModel(false);
            setSelectedElement(null);
          }}
          afterEdit={() => {
            setEditModel(false);
            setSelectedElement(null);
          }}
          templateId={templateId}
          elements={filteredElements}
          selectedElementCategory={selectedElementCategory}
          selectedElement={selectedElement}
        />
      )}
    </>
  );
}

export default ElementSection;
