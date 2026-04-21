
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from mServices import ResponseService, QueryBuilderService, ValidatorService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from envoy_bu_crm_api.service import handle_entity, handle_entity_notes, handle_entity_docs

POLICY_CONFIG = {
    'request': {
        'id_field': 'request_policy_id',
        'exists_table': 'crmp_request_policies',
    },
    'issued': {
        'id_field': 'issued_policy_id',
        'exists_table': 'crmp_issued_policies',
    }
}

CATEGORY_MAP = {
    'policy-related': 'Policy-Related',
    'risk-related': 'Risk-Related',
}


def get_validation_rules(policy_type):
    cfg = POLICY_CONFIG[policy_type]
    return {
        'file_name': 'required|string|max:255',
        'document_type': 'string|max:255',
        'notes': 'string',
        'document_category': 'required|in:Policy-Related,Risk-Related',
        cfg['id_field']: f"required|integer|exists:{cfg['exists_table']},id",
        'file': 'required|string',
    }
    
def get_validation_rules_put(policy_type):
    return {
        'file_name': 'required|string|max:255',
        'notes': 'string',
    }


def _authorize(request, action_key):
    action = ActionService.getAction('Documents', action_key)
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
    return None


def _get_documents(request, policy_type, policy_id=None, document_id=None, category=None):
    # Authorization
    if resp := _authorize(request, 'VIEW'):
        return resp

    # Build base query
    columns = [
        'crmp_documents.*',
        'core_entities.created_at as created_at',
        'core_users.display_name as created_by',
        'core_users.picture as created_logo',
        'core_entity_docs.doc as doc',
        'core_entity_docs.name as file_name',
        'core_entity_docs.type as file_type',
        "core_entity_notes.notes as notes",
    ]
    query = (QueryBuilderService('crmp_documents').select(*columns)
             .leftJoin('core_entities', 'core_entities.id', 'crmp_documents.entity_id')
             .leftJoin('core_users', 'core_users.id', 'core_entities.created_by_id')
             .leftJoin('core_entity_notes', 'core_entity_notes.entity_id', 'crmp_documents.entity_id')
             .leftJoin('core_entity_docs', 'core_entity_docs.entity_id', 'crmp_documents.entity_id'))

    cfg = POLICY_CONFIG[policy_type]
    # Apply filters
    if policy_id is not None:
        query = query.where(f"crmp_documents.{cfg['id_field']}", policy_id)
    if category is not None:
        query = query.where('crmp_documents.document_category', category)
    if document_id is not None:
        data = query.where('crmp_documents.id', document_id).first()
        if not data:
            return ResponseService.response('NOT_FOUND', None, Error.NOT_FOUND)
        return ResponseService.response('SUCCESS', data, Message.DATA_FETCHED)

    # Pagination, search, sort
    page     = int(request.GET.get('page', 1))
    limit    = int(request.GET.get('limit', 10))
    search   = request.GET.get('search', '')
    sort_by  = request.GET.get('sort_by', 'crmp_documents.id')
    sort_dir = request.GET.get('sort_dir', 'desc')
    filter_j = json.loads(request.GET.get('filter', '{}'))
    allowed_filters = [
        'crmp_documents.file_name',
        'crmp_documents.document_type',
        'crmp_documents.document_category',
    ]
    search_columns = ['crmp_documents.file_name', 'crmp_documents.document_type']
    sort_columns   = ['crmp_documents.id', 'core_entities.created_at']

    data = (query
            .apply_conditions(filter_j, allowed_filters, search, search_columns)
            .paginate(page, limit, sort_columns, sort_by, sort_dir))
    return ResponseService.response('SUCCESS', data, Message.DATA_FETCHED)


def _create_document(request, policy_type):
    if resp := _authorize(request, 'CREATE'):
        return resp

    data = json.loads(request.body or '{}')
    rules = get_validation_rules(policy_type)
    if errors := ValidatorService.validate(data, rules):
        return ResponseService.response('VALIDATION_ERROR', errors, Error.VALIDATION_ERROR)

    user = request.user if request.user.is_authenticated else None
    entity = {'type': 'document', 'approvel_status': False}
    entity_id = handle_entity(entity, entity_id=data.get('entity_id'), user=user)

    cfg = POLICY_CONFIG[policy_type]
    data.update({
        'entity_id': entity_id,
        cfg['id_field']: data.get(cfg['id_field'])
    })
    created = QueryBuilderService('crmp_documents').insert(data)

    if notes := data.get('notes'):
        note = {'note': notes, 'created_by_id': user.id if user else None, 'created_at': data.get('uploaded_on')}
        handle_entity_notes(entity_id, [note])
    if doc_str := data.get('file'):
        handle_entity_docs(entity_id=entity_id,
                          docs=[{'doc': doc_str, 'name': data.get('file_name',''), 'type': data.get('document_type','')}])

    return ResponseService.response('SUCCESS', created, Message.DATA_FETCHED)


def _update_document(request, document_id):
    if resp := _authorize(request, 'UPDATE'):
        return resp

    data = json.loads(request.body or '{}')
    # Determine policy_type via existing record if needed (validation rules not re-checked here)
    if errors := ValidatorService.validate(data, get_validation_rules_put('issued')):  
        return ResponseService.response('VALIDATION_ERROR', errors, Error.VALIDATION_ERROR)

    # updated = QueryBuilderService('crmp_documents').where('id', document_id).update(data)
    # if not updated:
    #     return ResponseService.response('NOT_FOUND', None, Error.NOT_FOUND)

    doc = QueryBuilderService('crmp_documents').where('id', document_id).first()
    if entity_id := doc.get('entity_id'):
        handle_entity({'approvel_status': False}, entity_id=entity_id, user=request.user)
        
        note = {'note': data.get('notes'), 'created_by_id': request.user.id if request.user.is_authenticated else None,
                    'created_at': data.get('uploaded_on')}
        handle_entity_notes(entity_id, [note], is_update=True)
        if doc_str := data.get('file_name'):
            print('doc_str', entity_id)
            handle_entity_docs(entity_id=entity_id,
                              docs=[{ 'name': data.get('file_name')}],is_update=True)

    return ResponseService.response('SUCCESS', None, Message.DATA_FETCHED)


def _delete_document(request, document_id):
    if resp := _authorize(request, 'DELETE'):
        return resp

    deleted = QueryBuilderService('crmp_documents').where('id', document_id).delete()
    if deleted:
        return ResponseService.response('SUCCESS', {'id': document_id}, 'Deleted successfully')
    return ResponseService.response('NOT_FOUND', None, Error.NOT_FOUND)


def _bulk_create(request, policy_type):
    if resp := _authorize(request, 'CREATE'):
        return resp

    payload = json.loads(request.body or '{}')
    docs = payload.get('documents', [])
    cfg = POLICY_CONFIG[policy_type]
    policy_id = payload.get(cfg['id_field'])

    if not isinstance(docs, list) or not docs:
        return ResponseService.response('VALIDATION_ERROR', {'documents': 'must be a non-empty list'}, Error.VALIDATION_ERROR)

    created_list = []
    user = request.user if request.user.is_authenticated else None
    for idx, doc in enumerate(docs):
        doc.update({cfg['id_field']: policy_id})
        if errors := ValidatorService.validate(doc, get_validation_rules(policy_type)):
            return ResponseService.response('VALIDATION_ERROR', {f'documents[{idx}]': errors}, Error.VALIDATION_ERROR)

        entity = {'type': 'document', 'approvel_status': False}
        entity_id = handle_entity(entity, entity_id=None, user=user)
        doc.update({'entity_id': entity_id})
        created = QueryBuilderService('crmp_documents').insert(doc)
        created_list.append(created)

        if notes := doc.get('notes'):
            note = {'note': notes, 'created_by_id': user.id if user else None, 'created_at': doc.get('uploaded_on')}
            handle_entity_notes(entity_id, [note])
        if doc_str := doc.get('file'):
            handle_entity_docs(entity_id=entity_id,
                              docs=[{'doc': doc_str, 'name': doc.get('file_name',''), 'type': doc.get('document_type','')}])

    return ResponseService.response('SUCCESS', created_list, Message.DATA_FETCHED)

# Request-Policy Endpoints
@csrf_exempt
@api_view(['GET'])
def request_policy_document_list(request, request_policy_id):
    return _get_documents(request, 'request', policy_id=request_policy_id)

@csrf_exempt
@api_view(['GET'])
def request_documents_by_category(request, category):
    cat = CATEGORY_MAP.get(category.lower())
    if not cat:
        return ResponseService.response('VALIDATION_ERROR', {'document_category': f"Invalid category '{category}'"}, Error.VALIDATION_ERROR)
    return _get_documents(request, 'request', category=cat)

@csrf_exempt
@api_view(['GET'])
def request_documents_by_policy_and_category(request, request_policy_id, category):
    cat = CATEGORY_MAP.get(category.lower())
    if not cat:
        return ResponseService.response('VALIDATION_ERROR', {'document_category': f"Invalid category '{category}'"}, Error.VALIDATION_ERROR)
    return _get_documents(request, 'request', policy_id=request_policy_id, category=cat)

@csrf_exempt
@api_view(['POST'])
def request_policy_document_create(request):
    return _create_document(request, 'request')

@csrf_exempt
@api_view(['GET','PUT','DELETE'])
def request_policy_document(request,policy_type, document_id):

     if request.method == "GET":
        return _get_documents(request,policy_type=policy_type, document_id=document_id)
     elif request.method == "PUT":
        return _update_document(request, document_id)
     elif request.method == "DELETE":
        return _delete_document(request,document_id=document_id)

@csrf_exempt
@api_view(['DELETE'])
def request_policy_document_delete(request, document_id):
    return _delete_document(request, document_id)

@csrf_exempt
@api_view(['POST'])
def request_policy_documents_bulk_create(request):
    return _bulk_create(request, 'request')

# Issued-Policy Endpoints
@csrf_exempt
@api_view(['GET','PUT'])
def policy_document_list(request, policy_id):
    if request.method == "GET":
            return _get_documents(request, 'issued', policy_id=policy_id)

    elif request.method == "PUT":
        return _update_document(request, policy_id)

@csrf_exempt
@api_view(['GET'])
def documents_by_category(request, category):
    cat = CATEGORY_MAP.get(category.lower())
    if not cat:
        return ResponseService.response('VALIDATION_ERROR', {'document_category': f"Invalid category '{category}'"}, Error.VALIDATION_ERROR)
    return _get_documents(request, 'issued', category=cat)

@csrf_exempt
@api_view(['GET'])
def documents_by_policy_and_category(request, policy_id, category):
    cat = CATEGORY_MAP.get(category.lower())
    if not cat:
        return ResponseService.response('VALIDATION_ERROR', {'document_category': f"Invalid category '{category}'"}, Error.VALIDATION_ERROR)
    return _get_documents(request, 'issued', policy_id=policy_id, category=cat)

@csrf_exempt
@api_view(['POST'])
def policy_document_create(request):
    return _create_document(request, 'issued')

@csrf_exempt
@api_view(['PUT'])
def policy_document_update(request, document_id):
    return _update_document(request, document_id)

@csrf_exempt
@api_view(['DELETE'])
def policy_document_delete(request, document_id):
    return _delete_document(request, document_id)

@csrf_exempt
@api_view(['POST'])
def policy_documents_bulk_create(request):
    return _bulk_create(request, 'issued')
