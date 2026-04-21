import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import React, { useState, useRef, useEffect } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { useRouter } from 'next/navigation';

const OrgNodeCard = ({
  nodeDatum,
  setNodeId,
  handleOnDelete,
  rootId,
  setCreateFormVisible,
  setCurrentEditId,
}: {
  nodeDatum: any;
  setNodeId: Function;
  handleOnDelete: Function;
  rootId: any;
  setCreateFormVisible: Function;
  setCurrentEditId: Function;
}) => {
  const t = useTrans('label.org_nodes,otr.common');
  const [pop, setPop] = useState(false);
  const popRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  console.log(setNodeId);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (popRef.current && !popRef.current.contains(event.target as Node)) {
        setPop(false);
      }
    };

    if (pop) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [pop]);

  return (
    <g>
      <foreignObject width="220" height="130" x="-100" y="-65">
        <div className={`node-card ${rootId.toString() === nodeDatum.id?.toString() ? 'border border-2 border-primary' : ''}`} ref={popRef}>
          <div className="node-header">
            <Dropdown
              width="20"
              trigger={
                <span className="action-icon">
                  <Flexicon icon="dots-horizontal" variant="line" size={18} />
                </span>
              }
            >
              {(onClose: Function) => (
                <span className="t-action">
                  <DropdownItem
                    onClick={() => {
                      onClose();
                      // setNodeId(nodeDatum.id);
                      setCreateFormVisible(true);
                    }}
                  >
                    <span className="d-flex gap-2">
                      <Flexicon icon="eye" variant="line" size={17} />
                      <span>{t('add_node')}</span>
                    </span>
                  </DropdownItem>
                  <DropdownItem onClick={() => (onClose(), router.push(`/a/nodes/${1}`))}>
                    <span className="d-flex gap-2">
                      <Flexicon icon="eye" variant="line" size={17} />
                      <span>{t('view')}</span>
                    </span>
                  </DropdownItem>
                  <DropdownItem onClick={() => (onClose(), setCurrentEditId(1))}>
                    <span className="d-flex gap-2">
                      <Flexicon icon="pencil-line" variant="line" size={17} />
                      <span>{t('edit')}</span>
                    </span>
                  </DropdownItem>
                  <DeleteConfirmPop
                    trigger={
                      <DropdownItem>
                        <span className="d-flex gap-2 w-100">
                          <Flexicon icon="trash-03" variant="line" size={17} />
                          <span>{t('delete')}</span>
                        </span>
                      </DropdownItem>
                    }
                    deleteId={nodeDatum.id}
                    {...{ handleOnDelete, onClose }}
                  />
                  {/* {nodeDatum.id !== undefined && (
                    <DeleteConfirmPop
                      trigger={
                        <DropdownItem>
                          <span className="d-flex gap-2 w-100">
                            <Flexicon icon="trash-03" variant="line" size={17} />
                            <span>{t('delete')}</span>
                          </span>
                        </DropdownItem>
                      }
                      deleteId={nodeDatum.id}
                      {...{ handleOnDelete, onClose }}
                    />
                  )} */}
                </span>
              )}
            </Dropdown>
          </div>
          <div className="node-content">
            <p className="node-title">{nodeDatum.name}</p>
            <p className="node-subtitle">{nodeDatum.type}</p>
          </div>
        </div>
      </foreignObject>
    </g>
  );
};

export default OrgNodeCard;
