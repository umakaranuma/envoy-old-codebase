import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type GAParams = {
  search?: string;
  page?: string;
  limit?: string;
  sort_by?: string;
  sort_dir?: string;
  filters?: string;
  status?: string;
  type?: string;
  stage_id?: string;
  sales_agent_id?: string;
  ids?: string;
  opportunityId?: string;
  ignore?: string;
  fields?: string;
  lead_id?: string;
  stage_type?: string;
  quotation?: string;
  risk_type_id?: string;
};

export async function getOpportunityStages(params?: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-statuses?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllChannels(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/channels?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllOpportunityTypes(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types?${queryString}`,
      method: 'GET',
    }),
  );
}

// ids: opportunity id
export async function getManyOpportunityTypes(ids: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/many?ids=${ids}`,
      method: 'GET',
    }),
  );
}

export async function getAllSalesAgents(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/sales-agents?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllCurrencies(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/currencies?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getOneCurrency(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/currencies/${id}`,
      method: 'GET',
    }),
  );
}

export async function getOneHealth(id: string, health_id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${id}/health/${health_id}`,
      method: 'GET',
    }),
  );
}

export async function getAllCustomers(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/customers?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllContacts(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/contacts?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllOpportunities(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneOpportunity(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${id}`,
      method: 'GET',
    }),
  );
}

export async function getOneOpportunityState(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-statuses/${id}`,
      method: 'GET',
    }),
  );
}

export async function getOneChannel(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/channels/${id}`,
      method: 'GET',
    }),
  );
}

export async function getOneCountry(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/countries/${id}`,
      method: 'GET',
    }),
  );
}

export async function createOpportunity(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getOneContacts(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/contacts/${id}`,
      method: 'GET',
    }),
  );
}

export async function getOneCustomers(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/customers/${id}`,
      method: 'GET',
    }),
  );
}

export async function updateOpportunity(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${id}`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}

export async function deleteOpportunity(id: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function updateOpportunityStatus(opportunityId: string, formData: any) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${opportunityId}/status`,
      method: 'PATCH',
      data: formData,
    }),
  );
}

export async function createOpportunityType(formData: any, id: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${id}/types`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getAllTypesOfOpportunity(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${id}/types`,
      method: 'GET',
    }),
  );
}

export async function deleteOpportunityType(opportunityId: any, id: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${opportunityId}/types/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getAllOpportunityCollectedInfo(params: GAParams, opportunityId: string, formConfigId: string) {
  const queryString = new URLSearchParams(params).toString();
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${opportunityId}/form-config/${formConfigId}/info?${queryString}`,
    method: 'GET',
    abortDuplicate: true,
  });

  return responseHandling(response);
}

export async function deleteRiskInfo(submissionId: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/risk-details/${submissionId}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getOneOpportunityCollectedInfo(opportunityId: string, submissionId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${opportunityId}/form-submission/${submissionId}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
}

export async function editOpportunityCollectedInfo(opportunityId: string, submissionId: string, formData: any) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${opportunityId}/form-submission/${submissionId}`,
      method: 'PUT',
      data: formData,
    }),
  );
}

export async function getAllOpportunityTypeConfig(opportunityTypeId: string, data_gethering_type: 'ONBOARDING') {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${opportunityTypeId}/form-config?data_gethering_type=${data_gethering_type}`,
    method: 'GET',
    abortDuplicate: true,
  });

  return responseHandling(response);
}

export async function getAllOpportunityTypeFormAttributes(formId: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${formId}/elements`,
    method: 'GET',
    abortDuplicate: true,
  });

  return responseHandling(response);
}

export async function getAllFormsDetails(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/templates/${id}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
}

export async function addOpportunityCollectedInfo(opportunityId: string, formConfigId: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${opportunityId}/form-config/${formConfigId}/info`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getAllHealthOfOpportunity(id: string, sort_dir?: string, sort_by?: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${id}/health?sort_dir=${sort_dir}&sort_by=${sort_by}`,
      method: 'GET',
    }),
  );
}

export async function addHealthOfOp(opportunityId: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${opportunityId}/health`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getAllInterestedProducts(params: GAParams, id: string, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${id}/interested-products?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllProducts(params: GAParams, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/products?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function createInterestedProduct(opportunityId: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${opportunityId}/interested-products`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function deleteInterestedProduct(opportunityId: any, id: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${opportunityId}/interested-products/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function updateOpInteraction(id: string, formData: any, intId: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${id}/interactions/${intId}`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}

export async function getAllOpInteractions(params: GAParams, id: any, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${id}/interactions?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllPolicies(params: GAParams, lead_id: any, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${lead_id}/issued-policies?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function createOpInteraction(opportunityId: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${opportunityId}/interactions`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getOneOpInteraction(opId: string, id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${opId}/interactions/${id}`,
      method: 'GET',
    }),
  );
}

export async function deleteOpInteraction(opportunityId: any, id: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${opportunityId}/interactions/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function addDocuments(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/entities/${id}/documents`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteDocument(entityId: any, id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/entities/${entityId}/documents/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getAllDocuments(entityId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/entities/${entityId}/documents`,
      method: 'GET',
    }),
  );
}

export async function getAllNotesOfOpportunity(params: GAParams, id: string, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/entities/${id}/notes?${queryString}`,
      method: 'GET',
      abortDuplicate,
    }),
  );
}

export async function createNotes(formData: any, id: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/entities/${id}/notes`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getOneNotes(id: string, notes_id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/entities/${id}/notes/${notes_id}`,
      method: 'GET',
    }),
  );
}

export async function updateNotes(id: string, notes_id: string, formData: any) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/entities/${id}/notes/${notes_id}`,
      method: 'PUT',
      data: formData,
    }),
  );
}

export async function deleteNotes(id: string, notes_id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}//api/entities/${id}/notes/${notes_id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getAllAcountManger(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/users?${queryString}`,
      method: 'GET',
    }),
  );
}

//Flag
export async function createFlag(entityId: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/entities/${entityId}/flags`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getAllFlagType(params: GAParams, entityId: string, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/flags?entity_id=${entityId}?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllReasons(params: GAParams, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/reasons?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneEntities(params: string, entityId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/entities/${entityId}?attri=${params}`,
      method: 'GET',
    }),
  );
}

export async function deleteEntityFlag(entityId: string, flag_id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/entities/${entityId}/flags/${flag_id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

// Leads History
export async function getAllEntitiesActivities(entityId: string, formData?: string, toData?: string, sort_dir?: string, limit?: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/entities/${entityId}/activities?from_date=${formData}&to_date=${toData}&sort_dir=${sort_dir}&limit=${limit}`,
    method: 'GET',
  });

  return responseHandling(response);
}

export async function updateOpportunityCustomer(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${id}/customer`,
    method: 'PATCH',
    data: formData,
  });

  return responseHandling(response);
}

export async function getAllCountries(params: GAParams, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/countries?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllRiskInfo(params: GAParams, abortDuplicate: boolean, riskTypeId: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/lead-risk/${riskTypeId}?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function CreateRiskInfo(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/lead-risks`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getOneRiskInfo(risk_detail_id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/risk-details/${risk_detail_id}`,
      method: 'GET',
    }),
  );
}

export async function updateOneRiskInfo(risk_detail_id: string, formData: any) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/risk-details/${risk_detail_id}`,
      method: 'PUT',
      data: formData,
    }),
  );
}

export async function createFormConfig(id: any, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${id}/forms`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getAllForms(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/templates?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllIssuedPolicies(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllProductsByType(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/native-product-by-type?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllSalesAgentHistories(params: GAParams, id: any, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${id}/sales-agent-history?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}
