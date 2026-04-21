import dynamic from 'next/dynamic';
const Tree = dynamic(() => import('react-d3-tree'), { ssr: false, loading: () => <Skeleton height="400px" /> });
import { useEffect, useState } from 'react';
import CreateNode from './CreateNode';
import OrgNodeCard from './OrgNodeCard';
import { Skeleton } from '@apptimus-ui/ui-element';
import { EditNode } from './EditNode';

type ComponentProps = {
  data: any;
  name: any;
  type: any;
  afterNodeCreation: any;
  id: any;
};

export default function TeamView({ data, name, afterNodeCreation, id }: ComponentProps) {
  const [_nodeId, setNodeId] = useState('');
  const [createFormVers, _setCreateFormVers] = useState(0);
  const [translate, setTranslate] = useState({ x: 0, y: 0 });
  // const tBe = useTrans('be.msg,be.error,be.attri');
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [currentEditId, setCurrentEditId] = useState('');

  console.log(afterNodeCreation, id);

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
    console.log('Delete ID:', deleteId);
    console.log('setLoader', setLoader);

    // if (!deleteId) {
    //   console.error('Error: Node ID is undefined');
    //   return;
    // }

    // setLoader(true);
    // const responseData = await deleteHierarchies(deleteId);
    // setLoader(false);

    // if (responseData.is_success) {
    //   toaster.success(tBe(responseData.message));
    //   afterNodeCreation();
    // }
  };

  const treeData: any = data ? { root: data.name, children: data.children || [] } : null;

  return (
    <div id="tree-container" className="hierarchy-tree-container overflow-hidden">
      <Tree
        data={treeData}
        orientation="vertical"
        translate={translate}
        zoom={0.5} // Adjust zoom level as needed
        renderCustomNodeElement={(rd) => (
          <OrgNodeCard
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
            setCreateFormVisible={setCreateFormVisible}
            setCurrentEditId={setCurrentEditId}
            handleOnDelete={handleOnDelete}
          />
        )}
        separation={{ siblings: 2, nonSiblings: 2 }} // Adjust space between nodes
        nodeSize={{ x: 150, y: 250 }} // Increase space between nodes
      />

      {createFormVisible && <CreateNode isOpen={createFormVisible} key={createFormVers} onCancel={() => setCreateFormVisible(false)} afterSave={() => {}} />}
      {!!currentEditId && <EditNode isOpen={!!currentEditId} onCancel={() => setCurrentEditId('')} afterEdit={() => setCurrentEditId('')} editId={currentEditId} />}
    </div>
  );
}
