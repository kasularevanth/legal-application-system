"""
Form template definitions for common legal applications
"""

PETITION_TEMPLATE = {
    "name": "Civil Petition",
    "form_type": "petition",
    "description": "Template for filing civil petitions in court",
    "fields": [
        {
            "field_name": "petitioner_name",
            "field_type": "text",
            "label": "Petitioner Name",
            "description": "Full name of the petitioner",
            "is_required": True,
            "order": 1
        },
        {
            "field_name": "petitioner_address",
            "field_type": "textarea",
            "label": "Petitioner Address",
            "description": "Complete address of the petitioner",
            "is_required": True,
            "order": 2
        },
        {
            "field_name": "respondent_name",
            "field_type": "text",
            "label": "Respondent Name",
            "description": "Full name of the respondent",
            "is_required": True,
            "order": 3
        },
        {
            "field_name": "case_facts",
            "field_type": "textarea",
            "label": "Statement of Facts",
            "description": "Brief facts of the case",
            "is_required": True,
            "order": 4
        },
        {
            "field_name": "relief_sought",
            "field_type": "textarea",
            "label": "Relief Sought",
            "description": "What relief/remedy are you seeking from the court",
            "is_required": True,
            "order": 5
        },
        {
            "field_name": "case_value",
            "field_type": "number",
            "label": "Case Value (₹)",
            "description": "Monetary value of the case if applicable",
            "is_required": False,
            "order": 6
        }
    ],
    "legal_requirements": "This petition must be accompanied by required court fees, affidavit, and supporting documents as per CPC provisions.",
    "court_types": ["District Court", "High Court"]
}

BAIL_APPLICATION_TEMPLATE = {
    "name": "Bail Application",
    "form_type": "application",
    "description": "Application for bail in criminal matters",
    "fields": [
        {
            "field_name": "accused_name",
            "field_type": "text",
            "label": "Name of Accused",
            "description": "Full name of the accused person",
            "is_required": True,
            "order": 1
        },
        {
            "field_name": "fir_number",
            "field_type": "text",
            "label": "FIR Number",
            "description": "First Information Report number",
            "is_required": True,
            "order": 2
        },
        {
            "field_name": "police_station",
            "field_type": "text",
            "label": "Police Station",
            "description": "Name of the police station where FIR is registered",
            "is_required": True,
            "order": 3
        },
        {
            "field_name": "sections_applied",
            "field_type": "text",
            "label": "Sections Applied",
            "description": "IPC/other law sections applied in the case",
            "is_required": True,
            "order": 4
        },
        {
            "field_name": "grounds_for_bail",
            "field_type": "textarea",
            "label": "Grounds for Bail",
            "description": "Legal grounds on which bail is sought",
            "is_required": True,
            "order": 5
        },
        {
            "field_name": "surety_details",
            "field_type": "textarea",
            "label": "Surety Details",
            "description": "Details of proposed surety",
            "is_required": False,
            "order": 6
        }
    ],
    "legal_requirements": "Bail application must comply with Section 437/439 CrPC. Required documents: Copy of FIR, Charge sheet (if filed), Previous bail applications (if any).",
    "court_types": ["Magistrate Court", "Sessions Court", "High Court"]
}

CONSUMER_COMPLAINT_TEMPLATE = {
    "name": "Consumer Complaint",
    "form_type": "complaint",
    "description": "Complaint under Consumer Protection Act",
    "fields": [
        {
            "field_name": "complainant_name",
            "field_type": "text",
            "label": "Complainant Name",
            "description": "Name of the consumer filing complaint",
            "is_required": True,
            "order": 1
        },
        {
            "field_name": "service_provider",
            "field_type": "text",
            "label": "Service Provider/Seller",
            "description": "Name of the company/person against whom complaint is filed",
            "is_required": True,
            "order": 2
        },
        {
            "field_name": "transaction_date",
            "field_type": "date",
            "label": "Date of Purchase/Service",
            "description": "When was the product purchased or service availed",
            "is_required": True,
            "order": 3
        },
        {
            "field_name": "transaction_amount",
            "field_type": "number",
            "label": "Transaction Amount (₹)",
            "description": "Amount paid for the product/service",
            "is_required": True,
            "order": 4
        },
        {
            "field_name": "deficiency_details",
            "field_type": "textarea",
            "label": "Details of Service Deficiency",
            "description": "Explain the deficiency in service or product",
            "is_required": True,
            "order": 5
        },
        {
            "field_name": "compensation_sought",
            "field_type": "number",
            "label": "Compensation Sought (₹)",
            "description": "Amount of compensation demanded",
            "is_required": True,
            "order": 6
        }
    ],
    "legal_requirements": "Complaint must be filed within 2 years from the date of service deficiency. Required: Purchase receipt, correspondence with service provider.",
    "court_types": ["District Consumer Forum", "State Consumer Commission", "National Consumer Commission"]
}

LEGAL_TEMPLATES = [
    PETITION_TEMPLATE,
    BAIL_APPLICATION_TEMPLATE,
    CONSUMER_COMPLAINT_TEMPLATE
]