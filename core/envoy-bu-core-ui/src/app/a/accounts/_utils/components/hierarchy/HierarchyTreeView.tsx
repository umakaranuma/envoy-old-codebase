import dynamic from 'next/dynamic';
const Tree = dynamic(() => import('react-d3-tree'), { ssr: false });
import NodeCard from './NodeCard';
import { useEffect, useState } from 'react';
import { deleteHierarchies } from '../../api-service';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import AccountsCreate from '../AccountsCreate';

type ComponentProps = {
  data: any;
  name: any;
  type: any;
  afterNodeCreation: any;
  id: any;
};

export default function HierarchyTree({ data, name, afterNodeCreation, id }: ComponentProps) {
  const [nodeId, setNodeId] = useState('');
  const [createFormVers, setCreateFormVers] = useState(0);
  const [translate, setTranslate] = useState({ x: 0, y: 0 });
  const tBe = useTrans('be.msg,be.error,be.attri');

  useEffect(() => {
    const container = document.getElementById('tree-container');
    if (container) {
      setTranslate({
        x: container.clientWidth / 2, // Center horizontall
        y: 100, // Adjust vertical position
      });
    }
  }, []);

  const handleOnDelete = async (deleteId: string, setLoader: Function) => {
    if (!deleteId) {
      console.error('Error: Node ID is undefined');
      return;
    }

    setLoader(true);
    const responseData = await deleteHierarchies(deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      afterNodeCreation();
    }
  };

  const treeData: any = data ? { root: data.name, children: data.children || [] } : null;

  return (
    <div id="tree-container" className="hierarchy-tree-container">
      <Tree
        data={treeData}
        orientation="vertical"
        translate={translate}
        zoom={0.5} // Adjust zoom level as needed
        renderCustomNodeElement={(rd) => (
          <NodeCard
            rootId={data.id}
            nodeDatum={{
              ...rd.nodeDatum,
              name: rd.nodeDatum.name || name,
              // type: rd.nodeDatum.__rd3t || type,
            }}
            setNodeId={(id: string) => {
              if (!id) {
                setNodeId(data.id);
              } else {
                setNodeId(id);
              }
            }}
            handleOnDelete={handleOnDelete}
          />
        )}
        separation={{ siblings: 2, nonSiblings: 2 }} // Adjust space between nodes
        nodeSize={{ x: 150, y: 250 }} // Increase space between nodes
      />

      {nodeId !== '' && nodeId !== null && (
        <AccountsCreate
          isOpen={nodeId !== '' && nodeId !== null}
          key={createFormVers}
          onCancel={() => {
            setCreateFormVers((prev) => prev + 1);
            setNodeId('');
          }}
          afterSave={() => (afterNodeCreation(), setCreateFormVers((prev) => prev + 1), setNodeId(''))}
          parent_id={nodeId}
          id={id}
        />
      )}
    </div>
  );
}
