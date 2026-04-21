# Policy Fields Improvements Documentation

## Overview
This document outlines the improvements made to the `get_opportunities_with_policy_details` function in `envoy_bu_policy_api/policy/controllers/issued_policy_controller.py` to address missing policy-related fields and ensure proper naming consistency.

## Issues Identified

### 1. Missing Policy Fields
The original `standard_policy_fields` object was missing many important policy-related fields that are available in the database models but not included in the response structure.

### 2. Naming Inconsistencies
There were inconsistencies in field naming between policy data and quotation data, making it difficult to maintain a unified response structure.

### 3. Incomplete Field Coverage
The response object didn't cover all the fields that were being fetched in the database queries, leading to data loss.

## Improvements Made

### 1. Enhanced Standard Policy Fields Object

The `standard_policy_fields` object has been significantly expanded to include:

#### Basic Identification Fields
- `id`: Record identifier
- `code`: Policy/quotation code
- `policy_base_id`: Policy base record ID
- `policy_request_id`: Policy request ID

#### Request and Status Fields
- `requested_data`: Request data
- `status`: Current status
- `notes`: General notes
- `quotation_notes`: Quotation-specific notes
- `request_type`: Request type
- `request_type_id`: Request type ID
- `request_type_name`: Request type name

#### Entity and Relationship Fields
- `opportunity_id`: Related opportunity ID
- `entity_id`: Entity ID
- `lead_id`: Lead ID

#### Insurer/Service Provider Fields
- `insurer_id`: Insurer ID
- `insurer_name`: Insurer name
- `insurer_notes`: Insurer notes
- `service_provider_id`: Service provider ID
- `service_provider_name`: Service provider name
- `service_provider_description`: Service provider description
- `service_provider_logo`: Service provider logo
- `service_provider_email`: Service provider email
- `service_provider_status`: Service provider status
- `sp_status`: Service provider status (alternative)

#### Risk and Coverage Fields
- `risks`: Array of risk objects
- `risk_type_id`: Risk type ID
- `risk_type_name`: Risk type name
- `risk_details_form_id`: Risk details form ID
- `coverage_type_id`: Coverage type ID
- `coverage_type_name`: Coverage type name
- `coverage_details`: Coverage details
- `coverage_details_name`: Coverage details name

#### Financial Fields
- `sum_insured`: Sum insured amount
- `total_amount`: Total amount
- `premium_amount`: Premium amount
- `payment_mode_id`: Payment mode ID
- `payment_mode_name`: Payment mode name

#### Product Fields
- `product_id`: Product ID
- `product_name`: Product name

#### Date Fields
- `received_date`: Received date
- `quotation_issued_date`: Quotation issued date
- `expiry_date`: Expiry date
- `quotation_expiry_date`: Quotation expiry date
- `policy_start_date`: Policy start date
- `policy_expiry_date`: Policy expiry date

#### Request By Fields
- `request_by_id`: Request by user ID
- `request_by_name`: Request by user name

#### Customer Fields
- `customer_id`: Customer ID
- `customer_name`: Customer name
- `customer_logo`: Customer logo
- `customer_email`: Customer email
- `customer_address`: Customer address
- `customer_primary_contact`: Customer primary contact

#### Approval and Status Fields
- `approval_status`: Approval status
- `approved_user`: Approved user
- `approval_role`: Approval role
- `approval_level`: Approval level
- `approval_remarks`: Approval remarks
- `approval_date`: Approval date

#### Document Fields
- `quotation_document`: Quotation document
- `quotation_document_name`: Quotation document name
- `quotation_document_size`: Quotation document size
- `policy_document`: Policy document
- `policy_document_name`: Policy document name
- `policy_document_size`: Policy document size

#### Form Submission Fields
- `form_submission_id`: Form submission ID
- `by_user_id`: User who submitted
- `attribute_id`: Attribute ID
- `vendor_quotation_id`: Vendor quotation ID
- `send_quotation_id`: Send quotation ID

#### Property Fields (for quotation)
- `property_id`: Property ID
- `property_name`: Property name
- `property_description`: Property description

#### Version and Draft Fields
- `version`: Version number
- `is_received`: Is received flag
- `is_shortlisted`: Is shortlisted flag
- `is_draft`: Is draft flag
- `is_sent`: Is sent flag

#### Policy Type Indicator
- `is_policy`: Boolean indicating if this is a policy (True) or quotation (False)

### 2. Enhanced Policy Data Query

The policy base data query has been enhanced to include:
- Customer information with contact details
- Comprehensive insurer/service provider information
- All relevant policy fields with proper aliases
- Document information
- Risk and coverage details

### 3. Enhanced Quotation Data Query

The quotation data query has been improved to include:
- All service provider fields with proper mapping
- Approval information
- Property details
- Form submission data
- Version and status information

### 4. Improved Field Mapping

Both policy and quotation data processing now include:
- Comprehensive field mapping with fallbacks
- Proper field aliasing for consistency
- Null value handling
- Field validation and sanitization

### 5. Consistent Response Structure

The response structure now ensures:
- All fields are present in both policy and quotation responses
- Consistent naming across different data sources
- Proper field type handling
- Backward compatibility

## Benefits

1. **Complete Data Coverage**: All available policy and quotation fields are now included in the response
2. **Consistent Naming**: Unified field naming across policy and quotation data
3. **Better Maintainability**: Clear field organization and documentation
4. **Enhanced Functionality**: More comprehensive data available for frontend consumption
5. **Improved Debugging**: Better field visibility for troubleshooting

## Usage

The improved function now returns a comprehensive `policy_request` object for each opportunity that includes all relevant policy or quotation information with consistent field naming, making it easier for frontend applications to consume and display the data.

## Migration Notes

- Existing code using the `policy_request` object will continue to work
- New fields are added with default `None` values for backward compatibility
- Field aliases ensure existing field names still work
- The `is_policy` flag helps distinguish between policy and quotation data
