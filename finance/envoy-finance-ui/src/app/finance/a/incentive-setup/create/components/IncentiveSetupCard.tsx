'use client';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Select } from '@apptimus-ui/select';
import { Button, Input } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { ConditionNode, IPerformanceField, LogicGroupNode, LogicNode, LogicType } from '../../_utils/model';
import { AsyncSelectConfigData } from './AsyncSelectConfig';
import { useTrans } from '@/helpers/services/lang/langService';
import { RewardTypeCreate } from './RewardTypeCreate';
import { snakeToTitleCase } from '@/helpers/services/commonService';
// --- Helper Type Guards ---
function isLogicGroup(node: LogicNode): node is LogicGroupNode {
  return (node as LogicGroupNode).logic !== undefined;
}

// --- Logic Tree Builder Components ---
const ConditionRow: React.FC<{
  node: ConditionNode;
  onChange: (node: ConditionNode) => void;
  onRemove: () => void;
  fields: Array<{ value: string; values: any[]; label: string; description: string; operators: string[]; widget: string }>;
  errors?: { field?: boolean; operator?: boolean; value?: boolean };
  isView: boolean;
  openRewardTypeModal: (path: number[]) => void;
  path: number[];
}> = ({ node, onChange, onRemove, fields, errors, isView, openRewardTypeModal, path }) => {
  const t = useTrans('label.incentive_setup,otr.common');
  // const currency = getCurrency();
  if (!fields || fields.length === 0) return null;
  const selectedField = fields.find((f) => f.value === node.field) || fields[0];
  if (!selectedField) return null;
  const operatorOptions = selectedField?.operators || [];
  // Find async config for this field
  const asyncConfig = AsyncSelectConfigData?.find((cfg) => cfg.field === selectedField.value);
  // const asyncUrl = asyncConfig?.url;
  const apilabel = asyncConfig?.label;
  const hasReward = node.reward_type || node.reward_type_value;
  const [showCustomInput, setShowCustomInput] = useState(node.label === 'Custom Value');
  const [customValueType, setCustomValueType] = useState<'fixed' | 'percentage'>(node.type || 'fixed');

  return (
    <div className="row g-2 g-md-3 g-lg-3 mb-4 ms-0 ms-md-4 align-items-center">
      <div className="col-12 col-md-4 custom-values">
        {isView ? (
          <Input value={snakeToTitleCase(node.field) || ''} disabled />
        ) : (
          <Select
            key={node.field}
            options={fields.map((f) => ({ id: f.value, label: f.label, description: f.description }))}
            defaultValue={
              fields.find((f) => f.value === node.field)
                ? { id: node.field, label: selectedField.label, description: selectedField.description }
                : fields.length
                  ? { id: fields[0].value, label: fields[0].label, description: fields[0].description }
                  : undefined
            }
            onChange={(_, data) => onChange({ ...node, field: data.id, operator: '' })}
            option={{
              label: 'label',
              value: 'id',
              keysToSearch: ['label', 'id'],
              // show description as native tooltip on hover
              labelFn: (option) => <div title={option.description || ''}>{option.label}</div>,
            }}
            className={`${errors?.field ? 'is-invalid' : ''} custom-container`}
            placeholder="Field"
            isSearchable={true}
          />
        )}
      </div>
      <div className="col-12 col-md-2 custom-values">
        {isView ? (
          <Input value={node.operator || ''} disabled />
        ) : (
          <Select
            key={node.operator}
            options={operatorOptions.map((op) => ({ id: op, label: op }))}
            defaultValue={
              operatorOptions.includes(node.operator) ? { id: node.operator, label: node.operator } : operatorOptions.length ? { id: operatorOptions[0], label: operatorOptions[0] } : undefined
            }
            onChange={(_, data) => onChange({ ...node, operator: data.id })}
            option={{
              label: 'label',
              value: 'id',
              keysToSearch: ['label', 'id'],
              labelFn: (option) => {
                const des = getOperatorDescription(option.label);
                return <div title={des || ''}>{option.label}</div>;
              },
            }}
            className={errors?.operator ? 'is-invalid custom-container' : 'custom-select custom-container'}
            placeholder="Operator"
            isSearchable={false}
          />
        )}
      </div>
      <div className="col-12 col-md-6 ">
        <div className="row">
          <div className="col-11">
            {isView ? (
              selectedField.widget === 'table' || selectedField.widget === 'dropdown' ? (
                <Input value={node.label || ''} disabled />
              ) : (
                <Input value={node.type === 'percentage' ? `${node.value || ''}` : `${node.value || ''}`} disabled />
              )
            ) : selectedField.widget === 'table' || selectedField.widget === 'dropdown' || selectedField.widget === 'number_with_options' ? (
              <div className="d-flex gap-2 align-items-center">
                <div className="w-100">
                  <Select
                    key={`dropdown-${node.field}-${selectedField.value}`}
                    defaultValue={
                      node.value && node.field === selectedField.value
                        ? {
                            id: node.value,
                            [asyncConfig?.label || 'label']: node.label,
                          }
                        : undefined
                    }
                    onChange={(_, data) => {
                      console.log('data', data);
                      const isCustom = data?.id === 'custom_value';
                      setShowCustomInput(isCustom);

                      onChange({
                        ...node,
                        value: isCustom ? '' : data?.id,
                        label: data?.[apilabel || 'label'],
                        type: isCustom ? 'fixed' : node.type,
                      });
                    }}
                    options={selectedField.values}
                    option={{
                      value: asyncConfig?.id || 'id',
                      label: asyncConfig?.label || 'label',
                    }}
                    className={errors?.value ? 'is-invalid' : 'custom-select'}
                    placeholder={selectedField.widget === 'table' ? 'Select record' : 'Select option'}
                    isSearchable={false}
                  />
                </div>
                {selectedField.widget === 'number_with_options' && showCustomInput && (
                  <>
                    <div style={{ minWidth: '150px' }}>
                      <Input
                        className={`form-control${errors?.value ? ' is-invalid' : ''}`}
                        type="number"
                        value={node.value || ''}
                        onChange={(e) => onChange({ ...node, value: e.target.value, label: 'Custom Value', type: customValueType })}
                        placeholder="Enter custom value"
                      />
                    </div>
                    <div style={{ minWidth: '130px' }}>
                      <Select
                        key={`custom-type-${customValueType}`}
                        defaultValue={{ id: customValueType, label: customValueType === 'fixed' ? 'Fixed' : 'Percentage' }}
                        onChange={(_, data) => {
                          const newType = data.id as 'fixed' | 'percentage';
                          setCustomValueType(newType);
                          onChange({ ...node, type: newType });
                        }}
                        options={[
                          { id: 'fixed', label: 'Fixed' },
                          { id: 'percentage', label: 'Percentage' },
                        ]}
                        option={{
                          label: 'label',
                          value: 'id',
                        }}
                        className="custom-select"
                        placeholder="Type"
                        isSearchable={false}
                      />
                    </div>
                  </>
                )}
              </div>
            ) : (
              // ) : (
              //   <Input
              //     className={`form-control${errors?.value ? ' is-invalid' : ''}`}
              //     type="number"
              //     value={node.value || ''}
              //     onChange={(e) => onChange({ ...node, value: e.target.value })}
              //     placeholder="Value"
              //   />
              // )
              <Input
                className={`form-control${errors?.value ? ' is-invalid' : ''}`}
                type="number"
                value={node.value || ''}
                onChange={(e) => onChange({ ...node, value: e.target.value })}
                placeholder="Value"
              />
            )}
          </div>
          {!isView && (
            <div className="col-1 mt-1">
              <Button color="danger" size="sm" onClick={onRemove}>
                <Flexicon icon="x-close" variant="line" size={16} />
              </Button>
            </div>
          )}
        </div>
      </div>
      <div className="col-12 col-md-12 col-lg-auto d-flex flex-wrap align-items-center gap-2 mt-2 mt-lg-3">
        {hasReward ? (
          <div className="d-flex align-items-center">
            <div className="fs-13 text-muted">
              {t('reward_type_value')}: {node.reward_type_value}
            </div>
            {!isView && (
              <div>
                <Flexicon icon="edit-02" variant="line" size={18} className="text-primary ms-2 pointer" onClick={() => openRewardTypeModal(path)} />
              </div>
            )}
          </div>
        ) : (
          !isView && (
            <Button color="primary" size="sm" onClick={() => openRewardTypeModal(path)}>
              <Flexicon icon="plus" variant="line" size={14} /> {t('add_reward_type')}
            </Button>
          )
        )}
      </div>
    </div>
  );
};

const NESTED_BG_COLORS = [
  '#f8fafc', // root - very light blue/gray
  '#e3f2fd', // level 1 - light blue
  '#e8f5e9', // level 2 - light green
  '#fff3e0', // level 3 - light orange
  '#f3e5f5', // level 4+ - light purple
];
const NESTED_BORDER_COLORS = [
  '#1976d2', // root - blue
  '#0288d1', // level 1 - cyan blue
  '#388e3c', // level 2 - green
  '#f57c00', // level 3 - orange
  '#8e24aa', // level 4+ - purple
];

const LogicGroup: React.FC<{
  node: LogicGroupNode;
  onChange: (node: LogicGroupNode) => void;
  onRemove?: () => void;
  fields: Array<{ value: string; values: any[]; label: string; description: string; operators: string[]; widget: string }>;
  depth?: number;
  errors?: any;
  isView: boolean;
  openRewardTypeModal: (path: number[]) => void;
  path: number[];
}> = ({ node, onChange, onRemove, fields, depth = 0, errors, isView, openRewardTypeModal, path }) => {
  const t = useTrans('label.incentive_setup,otr.common');
  // Add condition
  const addCondition = () => {
    const firstField = fields[0];
    onChange({
      ...node,
      conditions: [
        ...node.conditions,
        {
          field: firstField?.value || '',
          operator: firstField?.operators?.[0] || '',
          value: '',
          label: '',
        },
      ],
    });
  };
  // Add group
  const addGroup = () => {
    onChange({
      ...node,
      conditions: [...node.conditions, { logic: 'AND', conditions: [] }],
    });
  };

  // Update child
  const updateChild = (idx: number, child: LogicNode) => {
    let updatedChild = child;
    if (!isLogicGroup(child)) {
      // Always set operator to the first valid operator for the selected field
      const fieldDef = fields.find((f) => f.value === child.field) || fields[0];
      let newOperator = child.operator;
      if (child.operator === '' || !fieldDef?.operators?.includes(child.operator)) {
        newOperator = fieldDef?.operators?.[0] || '';
      }
      updatedChild = {
        ...child,
        field: fieldDef?.value || '',
        operator: newOperator,
      };
    }
    const newConds = node.conditions.slice();
    newConds[idx] = updatedChild;
    onChange({ ...node, conditions: newConds });
  };

  // Remove child
  const removeChild = (idx: number) => {
    const newConds = node.conditions.slice();
    newConds.splice(idx, 1);
    onChange({ ...node, conditions: newConds });
  };
  // Change logic type
  const changeLogic = (logic: LogicType) => {
    onChange({ ...node, logic });
  };
  const bgColor = NESTED_BG_COLORS[depth % NESTED_BG_COLORS.length];
  const borderColor = NESTED_BORDER_COLORS[depth % NESTED_BORDER_COLORS.length];
  const hasReward = node.reward_type || node.reward_type_value;
  const ml = Math.min(depth * 2, 5); // cap spacing util to available classes (0-5)
  const marginClass = depth ? `ms-md-${ml}` : '';
  return (
    <div
      className={`card mb-4 ${marginClass}`}
      style={{ borderLeft: depth ? `3px solid ${borderColor}` : undefined, background: bgColor, borderRadius: 16, boxShadow: '0 1px 4px rgba(0,0,0,0.03)', width: '100%' }}
    >
      <div className="card-body p-3 p-md-4">
        <div className="d-flex flex-wrap align-items-center mb-3 gap-2 gap-md-3">
          <span className="fw-bold text-primary">{t('group')}</span>
          <div style={{ minWidth: 80, maxWidth: 120 }}>
            {isView ? (
              <Input value={node.logic || ''} disabled />
            ) : (
              <Select
                key={node.logic}
                onChange={(_, data) => {
                  changeLogic(data.label as LogicType);
                }}
                defaultValue={{ id: node.logic === 'AND' ? 1 : 2, label: node.logic }}
                options={[
                  { id: 1, label: 'AND' },
                  { id: 2, label: 'OR' },
                ]}
                option={{
                  label: 'label',
                  value: 'id',
                  keysToSearch: ['label', 'id'],
                }}
              />
            )}
          </div>
          {node.conditions.length > 1 && (
            <>
              {hasReward ? (
                <div className="d-flex align-items-center">
                  <div className="text-muted fs-13">
                    {t('reward_type_value')}: {node.reward_type_value}
                  </div>
                  {!isView && (
                    <div>
                      <Flexicon icon="edit-02" variant="line" size={18} className="text-primary ms-2 pointer" onClick={() => openRewardTypeModal(path)} />
                    </div>
                  )}
                </div>
              ) : (
                !isView && (
                  <Button color="primary" size="sm" onClick={() => openRewardTypeModal(path)}>
                    <Flexicon icon="plus" variant="line" size={14} /> {t('add_reward_type')}
                  </Button>
                )
              )}
            </>
          )}
          {onRemove && !isView && (
            <Button color="danger" size="sm" onClick={onRemove}>
              <Flexicon icon="x-close" variant="line" size={14} />
            </Button>
          )}
        </div>
        <div className="mb-3 ">
          {node.conditions.map((cond, idx) =>
            isLogicGroup(cond) ? (
              <LogicGroup
                key={idx}
                node={cond}
                onChange={(child) => updateChild(idx, child)}
                onRemove={() => removeChild(idx)}
                fields={fields}
                depth={depth + 1}
                errors={errors?.[idx]}
                isView={isView}
                openRewardTypeModal={openRewardTypeModal}
                path={[...path, idx]}
              />
            ) : (
              <ConditionRow
                key={idx}
                node={cond}
                onChange={(child) => updateChild(idx, child)}
                onRemove={() => removeChild(idx)}
                fields={fields}
                errors={errors?.[idx]}
                isView={isView}
                openRewardTypeModal={openRewardTypeModal}
                path={[...path, idx]}
              />
            ),
          )}
        </div>
        {!isView && (
          <div className="d-flex flex-wrap gap-2 gap-md-3 mt-2">
            <Button color="primary" size="sm" onClick={addCondition}>
              <Flexicon icon="plus" variant="line" size={14} /> {t('add_condition')}
            </Button>
            <Button color="secondary" size="sm" onClick={addGroup}>
              <Flexicon icon="plus" variant="line" size={14} /> {t('add_nested_group')}
            </Button>
          </div>
        )}
        {errors?.group && <div className="err-msg mt-2">{t('each_group_must_have_at_least_one_condition_or_group')}</div>}
      </div>
    </div>
  );
};

// --- Validation ---
function validateLogicNode(node: LogicNode): any {
  if (isLogicGroup(node)) {
    const errors: any = [];
    if (!node.conditions.length) return { group: true };
    node.conditions.forEach((c, i) => {
      errors[i] = validateLogicNode(c);
    });
    return errors;
  } else {
    return {
      field: !node.field,
      operator: !node.operator,
      value: !node.value,
    };
  }
}

// --- Main IncentiveSetupCard Component ---
const IncentiveSetupCard = ({
  onUpdate,
  performanceFieldData,
  defultLogicTree,
  isView = false,
  error,
}: {
  onUpdate: (data: any) => void;
  performanceFieldData: IPerformanceField[];
  skeleton: boolean;
  defultLogicTree?: LogicGroupNode;
  isView?: boolean;
  error?: string;
}) => {
  const t = useTrans('label.incentive_setup,otr.common');

  // --- Logic Tree State ---
  const [logicTree, setLogicTree] = useState<LogicGroupNode>(defultLogicTree || { logic: 'AND', conditions: [] });
  const [logicTreeErrors, setLogicTreeErrors] = useState<any>(null);
  const [importError, setImportError] = useState<string>('');
  const fileInputRef = React.useRef<HTMLInputElement | null>(null);
  const [rewardModalOpen, setRewardModalOpen] = useState(false);
  const [rewardEditPath, setRewardEditPath] = useState<number[] | null>(null);

  // Dynamically generate FIELDS from performanceFieldData
  const FIELDS = performanceFieldData.map((f: any) => ({
    value: f.field,
    values: f.widget === 'number_with_options' ? [...(f.value_options?.map((vo: any) => ({ id: vo.id, label: vo.label })) || []), { id: 'custom_value', label: 'Custom Value' }] : f.values || [],
    label: f.field.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()), // or use f.description for label
    description: f.description,
    operators: f.operators,
    widget: f.widget,
  }));

  // --- Real-time validation ---
  React.useEffect(() => {
    setLogicTreeErrors(validateLogicNode(logicTree));
    onUpdate(logicTree);
  }, [logicTree]);

  // Handle JSON import
  const handleImportClick = () => {
    setImportError('');
    fileInputRef.current?.click();
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const parsed = JSON.parse(String(reader.result));

        // Basic structure check
        if (!parsed || typeof parsed !== 'object' || !('logic' in parsed) || !Array.isArray(parsed.conditions)) {
          setImportError('Invalid logic JSON structure');
          return;
        }

        // Run existing validator to ensure node structure is valid
        const validation = validateLogicNode(parsed);
        const hasErrors = (function checkErrors(err: any): boolean {
          if (!err) return false;
          if (Array.isArray(err)) return err.some((e) => checkErrors(e));
          if (typeof err === 'object') return Object.values(err).some((v) => v === true || checkErrors(v));
          return false;
        })(validation);

        if (hasErrors) {
          setImportError('Logic tree validation failed');
          return;
        }

        setLogicTree(parsed as LogicGroupNode);
        setLogicTreeErrors(null);
        setImportError('');
      } catch (err) {
        setImportError('Invalid JSON file');
      }
    };
    reader.readAsText(file);
    // reset input so same file can be uploaded again
    e.currentTarget.value = '';
  };

  // Export current logicTree as a downloadable JSON file
  const handleExportJson = () => {
    try {
      const content = JSON.stringify(logicTree, null, 2);
      const blob = new Blob([content], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'logic-tree.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      // fallback: do nothing or set importError
      setImportError('Failed to generate JSON file');
    }
  };

  const openRewardTypeModal = (path: number[]) => {
    setRewardEditPath(path);
    setRewardModalOpen(true);
  };

  function updateNodeAtPath(tree: LogicGroupNode, path: number[], rewardData: { reward_type: string; reward_type_value: number }): LogicGroupNode {
    // If reward_type_value is 0, remove reward_type and reward_type_value from the node
    const shouldRemoveReward = Number(rewardData.reward_type_value) === 0;
    if (path.length === 0) {
      if (shouldRemoveReward) {
        const { reward_type, reward_type_value, ...rest } = tree;
        return rest as LogicGroupNode;
      } else {
        return {
          ...tree,
          reward_type: rewardData.reward_type as 'fixed' | 'percentage',
          reward_type_value: rewardData.reward_type_value,
        };
      }
    }
    const [idx, ...rest] = path;
    return {
      ...tree,
      conditions: tree.conditions.map((cond, i) => {
        if (i !== idx) return cond;
        if ('conditions' in cond && rest.length > 0) {
          return updateNodeAtPath(cond as LogicGroupNode, rest, rewardData);
        }
        if (rest.length === 0) {
          if (shouldRemoveReward) {
            const { reward_type, reward_type_value, ...restCond } = cond;
            return restCond as LogicNode;
          } else {
            return {
              ...cond,
              reward_type: rewardData.reward_type as 'fixed' | 'percentage',
              reward_type_value: rewardData.reward_type_value,
            };
          }
        }
        return cond;
      }),
    };
  }

  function getNodeAtPath(tree: LogicGroupNode, path: number[]): LogicNode | null {
    if (path.length === 0) return tree;
    const [idx, ...rest] = path;
    if (!tree.conditions || !tree.conditions[idx]) return null;
    const child = tree.conditions[idx];
    if ('conditions' in child && rest.length > 0) {
      return getNodeAtPath(child as LogicGroupNode, rest);
    }
    if (rest.length === 0) {
      return child;
    }
    return null;
  }

  const node = rewardEditPath && rewardEditPath.length > 0 ? getNodeAtPath(logicTree, rewardEditPath) : logicTree;

  const intidata = {
    reward_type: node?.reward_type ?? 'fixed',
    reward_type_value: node?.reward_type_value ?? '',
  };

  return (
    <div className="">
      {/* --- Logic Tree Builder UI --- */}
      <div className="panel">
        <div className="d-flex flex-row flex-wrap justify-content-between align-items-start">
          <div>
            <div className="panel-title">{t('incentive_rule_logic_builder')}</div>
            <div className="panel-subtitle text-muted">{t('build_complex_nested_and_or_rules_for_incentives_add_groups_or_conditions_nest_as_needed_and_see_the_json_output_in_real_time')}</div>
            {importError && <div className="err-msg mt-2">{importError}</div>}
          </div>
          <div>
            <input ref={fileInputRef} type="file" onChange={handleFileUpload} style={{ display: 'none' }} />
            {!isView && (
              <Button color="light" size="sm" onClick={handleImportClick}>
                <Flexicon icon="upload-cloud-01" variant="line" size={16} />
                &nbsp;{t('import_json')}
              </Button>
            )}
          </div>
        </div>
        {error && <div className="err-msg mt-3">{error}</div>}
        <div style={{ background: '#f8f9fa', borderRadius: 12, padding: 20, border: '1px solid #e3e6ea' }} className="mt-3">
          <LogicGroup isView={isView} node={logicTree} onChange={setLogicTree} fields={FIELDS} depth={0} errors={logicTreeErrors} openRewardTypeModal={openRewardTypeModal} path={[]} />
        </div>
        <div className="mt-4">
          <div className="panel-subtitle text-muted">{t('resulting_logic_json')}</div>
          <pre className="bg-dark text-white p-3 rounded-3 small" style={{ maxHeight: 220, overflow: 'auto', fontSize: '0.95rem' }}>
            {JSON.stringify(logicTree, null, 2)}
          </pre>
          <div className="mt-2 d-flex justify-content-end">
            <Button color="light" size="sm" onClick={handleExportJson}>
              <Flexicon icon="download-01" variant="line" size={14} />
              &nbsp; {t('download')}
            </Button>
          </div>
        </div>
      </div>
      <RewardTypeCreate
        isOpen={rewardModalOpen}
        position={rewardEditPath}
        intidata={intidata}
        onCancel={() => setRewardModalOpen(false)}
        onSave={(rewardData: any, path: number[]) => {
          setLogicTree((prev) => updateNodeAtPath(prev, path, rewardData));
          setRewardModalOpen(false);
          setRewardEditPath(null);
        }}
      />
    </div>
  );
};

export default IncentiveSetupCard;

function getOperatorDescription(operator: string): string | null {
  const operatorDescriptions: { [key: string]: string } = {
    '=': 'Equal to',
    '>': 'Greater than',
    '<': 'Less than',
    '<=': 'Less than or equal to',
    '>=': 'Greater than or equal to',
    between: 'Between',
  };
  return operatorDescriptions[operator] || null;
}
