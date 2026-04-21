'use client';
import React, { useState } from 'react';
import { FieldMapping, ExcelFieldMapperProps } from './types';

const ExcelFieldMapper: React.FC<ExcelFieldMapperProps> = ({ systemFields, excelFields, onMappingChange }) => {
  const [mappings, setMappings] = useState<FieldMapping[]>(
    systemFields.map((field) => ({
      systemField: field.name,
      excelField: '',
      dataType: field.dataType,
    })),
  );

  const [draggedItem, setDraggedItem] = useState<{
    type: 'system' | 'excel';
    index: number;
  } | null>(null);

  const handleDragStart = (type: 'system' | 'excel', index: number) => {
    setDraggedItem({ type, index });
  };

  const handleDrop = (systemIndex: number) => {
    if (!draggedItem || draggedItem.type !== 'excel') return;

    const updatedMappings = [...mappings];
    updatedMappings[systemIndex].excelField = excelFields[draggedItem.index];
    setMappings(updatedMappings);
    onMappingChange(updatedMappings);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleClearMapping = (index: number) => {
    const updatedMappings = [...mappings];
    updatedMappings[index].excelField = '';
    setMappings(updatedMappings);
    onMappingChange(updatedMappings);
  };

  return (
    <div className="container-fluid mt-4">
      <div className="row">
        <div className="col-md-4">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h5 className="mb-0">Excel Fields</h5>
            </div>
            <div className="card-body p-0">
              <ul className="list-group list-group-flush">
                {excelFields.map((field, index) => (
                  <li key={field} draggable onDragStart={() => handleDragStart('excel', index)} className="list-group-item cursor-grab" style={{ cursor: 'grab' }}>
                    {field}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <div className="col-md-8">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h5 className="mb-0">Field Mappings</h5>
            </div>
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-hover mb-0">
                  <thead className="thead-light">
                    <tr>
                      <th>System Field Name</th>
                      <th>Excel Field Name</th>
                      <th>Data Type</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mappings.map((mapping, index) => (
                      <tr key={mapping.systemField} onDrop={() => handleDrop(index)} onDragOver={handleDragOver} className={mapping.excelField ? '' : 'table-warning'}>
                        <td>
                          <div draggable onDragStart={() => handleDragStart('system', index)} className="cursor-grab" style={{ cursor: 'grab' }}>
                            {mapping.systemField}
                          </div>
                        </td>
                        <td className={mapping.excelField ? 'text-success' : 'text-muted'} style={{ minWidth: '200px' }}>
                          {mapping.excelField || <span className="text-muted">Drop Excel field here</span>}
                        </td>
                        <td>{mapping.dataType}</td>
                        <td>
                          {mapping.excelField && (
                            <button onClick={() => handleClearMapping(index)} className="btn btn-sm btn-outline-danger">
                              Clear
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExcelFieldMapper;
