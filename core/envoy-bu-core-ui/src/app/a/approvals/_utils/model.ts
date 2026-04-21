export interface IApprovalService {
  total_records: number;
  per_page: number;
  current_page: number;
  last_page: number;
  data: IServiceProvider[];
}
export interface IServiceProvider {
  id: number;
  name: string;
  description: string | null;
  status: string;
  checked?: boolean;
}

export interface IApproval {
  entity_type: string;
  code: string;
  request_date: string;
  customer_id: number;
  status: string;
  notes: null;
  request_type: string;
  entity_id: number;
  opportunity_type_id: number;
  opportunity_id: number;
  opportunity_title: string;
  approval_id: number;
  approval_level: number;
  approval_status: string;
  approval_remarks: null;
  approval_date: string;
  created_by_name: string;
  approved_by_name: null;
  customer_name: string;
  opportunity_types: OpportunityType[];
  email_data: EmailData;
  document_data: any[];
  service_providers: IServiceProvider[];
}
export interface IServiceProvider {
  service_provider_id: number;
  service_provider_name: string;
  service_provider_status: string;
}

export interface OpportunityType {
  id: number;
  title: string;
}

export interface EmailData {
  body: string;
  files: File[];
  subject: string;
  defaultDocuments: DefaultDocument[];
  documents: IEmailDocument[];
}

export interface DefaultDocument {
  coverage_details: string;
  coverage_details_name: string;
}

export interface File {
  doc_link: string;
  doc_name: string;
  doc_type: string;
}

interface IEmailDocument {
  doc: string;
  name: string;
}
