import { ITablePropertyColumn } from '@/interface/ICommon';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Modal, ModalFooter } from '@apptimus-ui/modal';
import { Button, Input } from '@apptimus-ui/ui-element';
import Localbase from 'localbase';
import React, { useEffect, useState } from 'react';
import { SVG } from './SVG';
import { useTrans } from '@/helpers/services/lang/langService';

export const CustomizeColumn = ({
  isOpen,
  tableName,
  columns,
  onClose,
  afterUpdate,
}: {
  isOpen: boolean;
  tableName: string;
  columns: ITablePropertyColumn[];
  onClose: Function;
  afterUpdate: Function;
}) => {
  const t = useTrans('otr.common');
  const [items, setItems] = useState(columns as ITablePropertyColumn[]);
  const [searchValue, setSearchValue] = useState('');
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);

  const customizableColumns = items?.filter((item) => item.customizable);
  const selectedColumns = items?.filter((item) => !item.isHidden && item.customizable);

  useEffect(() => {
    setItems(columns);
  }, [columns]);

  const handleDragStart = (e: any, index: React.SetStateAction<number | null>) => {
    setDraggedIndex(index);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleCheckboxChange = (id: string) => {
    const updatedItems = items.map((item) => (item.id === id ? { ...item, isHidden: !item.isHidden } : item));

    setItems(updatedItems);
  };

  const handleDragOver = (e: any, index: number) => {
    e.preventDefault();

    if (draggedIndex === null) return;

    const newItems = [...items];
    const draggedItem = newItems[draggedIndex];
    newItems.splice(draggedIndex, 1);
    newItems.splice(index, 0, draggedItem);

    newItems.forEach((item, i) => {
      item.order = i + 1;
    });
    setItems(newItems);
    setDraggedIndex(index);
  };

  const onSubmit = async () => {
    const filteredItems = items?.filter((item) => item.customizable);
    const simplifiedItems = filteredItems.map(({ id, isHidden, order }) => ({ id: id, is_hidden: isHidden, order }));

    const db = new Localbase('tc_config');
    simplifiedItems.forEach((item) => db.collection(tableName).doc(item.id).set(item));

    afterUpdate();
    onClose();
  };

  const cancel = () => {
    setItems(columns);
    setSearchValue('');
    onClose();
  };

  const renderBody = () => {
    const sortedItems = items?.slice().sort((a, b) => {
      const orderA = a.order ?? 0;
      const orderB = b.order ?? 0;
      return orderA - orderB;
    });

    const filteredItems = sortedItems?.filter((item) => item.header?.toLowerCase().includes(searchValue.toLowerCase()));

    return (
      <>
        {filteredItems.length === 0 && <span className="d-flex justify-content-center text my-4">{t('no_records_found')}</span>}
        <ul className="available-column-list list-unstyled px-4 mb-0">
          {filteredItems?.map(
            (item, index) =>
              item.customizable && (
                <li
                  key={index}
                  className="cursor-move my-1 mx-0"
                  onClick={() => item.visibilityLock && handleCheckboxChange(item.id || '')}
                  draggable
                  onDragStart={(e) => handleDragStart(e, index)}
                  onDragOver={(e) => handleDragOver(e, index)}
                  onDrop={() => setDraggedIndex(null)}
                  style={{ background: draggedIndex === index ? '#dc731c78' : 'rgb(var(--light-rgb), 30%)' }}
                >
                  <div className="d-flex align-items-center gap-2">
                    <span className="d-flex text-muted">
                      <SVG icon="drag-indicator" width={18} height={18} />
                    </span>
                    {item.visibilityLock ? (
                      <Input type="checkbox" className="pointer w-13 h-13" checked={!item.isHidden} onChange={() => handleCheckboxChange(item.id || '')} />
                    ) : (
                      <span className="d-flex text opacity-70">
                        <Flexicon icon="lock-01" variant="line" size={18} />
                      </span>
                    )}
                    {item.header}
                  </div>
                </li>
              ),
          )}
        </ul>
      </>
    );
  };

  return (
    <>
      <Modal isOpen={isOpen} position="top">
        <div className="column-customize">
          <div className="d-flex justify-content-between align-items-center bg-light p-3">
            <div className="d-flex align-items-center gap-2">
              <Flexicon icon="settings-03" variant="line" size={18} />
              <h5 className="fs-18 fw-border mb-0">{t('customize_columns')}</h5>
            </div>
            <div className="d-flex align-items-center gap-2">
              <span className="fs-15">{t('selected_count', { selected: selectedColumns.length, total: customizableColumns.length })} </span>
              <span className="separationline h-16"></span>
              <span className="d-flex" onClick={cancel}>
                <Flexicon icon="x" variant="line" size={18} className="text-danger pointer" />
              </span>
            </div>
          </div>

          <div className="column-search pb-2 px-4 pt-4">
            <div className="input-group">
              <span className="input-group-text">
                <Flexicon icon="search-lg" variant="line" size={16} className="text-muted" />
              </span>
              <Input placeholder={t('search')} className="rounded-0 rounded-end form-control" value={searchValue} onChange={(e) => setSearchValue(e.target.value)} />
            </div>
          </div>
          {renderBody()}
        </div>

        <ModalFooter>
          <div className="d-flex gap-2 mx-3">
            <Button text={t('save')} width="sm" onClick={onSubmit} />
            <Button text={t('cancel')} color="light" width="sm" onClick={cancel} />
          </div>
        </ModalFooter>
      </Modal>
    </>
  );
};

export const useCustomizeColumn = ({ columns, tableName, tableColumnVers }: { columns: ITablePropertyColumn[]; tableName: string; tableColumnVers: any }) => {
  const [tableColumns, setTableColumns] = useState<ITablePropertyColumn[]>([]);

  useEffect(() => {
    let isMounted = true;

    const setData = async () => {
      try {
        const db = new Localbase('tc_config');
        let data: ITablePropertyColumn[] = [];

        // Fetch column configuration data from IndexedDB
        const collection = await db.collection(tableName).get();
        data = collection || [];

        // Update columns based on configuration from IndexedDB
        const updatedColumns = columns.map((column: ITablePropertyColumn, index: number) => {
          const existingData: any = data.find((item: any) => item.id === column.id);

          return {
            ...column,
            visibilityLock: column.visibilityLock === false ? false : true,
            customizable: column.customizable === false ? false : true,
            isHidden: existingData ? existingData.is_hidden : column.isHidden === true ? true : false,
            order: existingData ? existingData.order : index,
          };
        });

        const sortedColumns = [...updatedColumns].sort((a, b) => {
          const orderA = a.order ?? 0;
          const orderB = b.order ?? 0;
          return orderA - orderB;
        });

        if (isMounted) {
          setTableColumns(sortedColumns);
        }
      } catch (error) {
        console.error('Error fetching data from IndexedDB:', error);
        if (isMounted) {
          setTableColumns(columns);
        }
      }
    };

    setData();

    return () => {
      isMounted = false;
    };
  }, [tableColumnVers, tableName, columns]);

  return tableColumns;
};
