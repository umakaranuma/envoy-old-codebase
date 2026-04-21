export interface FieldMapping {
  systemField: string;
  excelField: string;
  dataType: string;
}

export interface ExcelFieldMapperProps {
  systemFields: { name: string; dataType: string }[];
  excelFields: string[];
  onMappingChange: (mappings: FieldMapping[]) => void;
}
