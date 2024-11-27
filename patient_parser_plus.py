#!/usr/bin/env python3

# Statistics
'''
 {'Patient': 1,
  'Organization': 1, 
  'Practitioner': 1,
  'Encounter': 16,
  'Condition': 3,
  'Claim': 18,
  'ExplanationOfBenefit': 16,
  'Observation': 94,
  'Immunization': 11,
  'DiagnosticReport': 5,
  'Procedure': 10,
  'MedicationRequest': 2,
  'CarePlan': 1,
  'ImagingStudy': 1})
'''

import json
from datetime import datetime
import typesense
import os
# from flask import Flask, request, jsonify

class EntityRetriever:
    def __init__(self, json_data):
        self.json_data = json_data

    def calculate_age(birthdate):
        birthdate = datetime.strptime(birthdate, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return age

    def get_patient_metadata(self, resource):
        # Extract id
        patient_id = resource.get('id')
        # Extract name
        name = resource.get('name', [{}])[0]
        full_name = f"{name.get('prefix', [''])[0]} {name.get('given', [''])[0]} {name.get('family', '')}".strip()

        # Extract identifiers
        identifiers = resource.get('identifier', [])
        identifier_map = {}
        for identifier in identifiers:
            display = identifier.get('type', {}).get('coding', [{}])[0].get('display')
            value = identifier.get('value')
            if display and value:
                identifier_map[display] = value

        # Extract extensions
        extensions = resource.get('extension', [])
        extension_map = {}
        for ext in extensions:
            url = ext.get('url')
            for sub_ext in ext.get('extension', []):
                if 'valueString' in sub_ext:
                    value = sub_ext['valueString']
                elif 'valueCode' in sub_ext:
                    value = sub_ext['valueCode']
                elif 'valueAddress' in sub_ext:
                    value = sub_ext['valueAddress']
                elif 'valueDecimal' in sub_ext:
                    value = sub_ext['valueDecimal']
                elif 'valueCoding' in sub_ext:
                    value = sub_ext['valueCoding']
                else:
                    value = None
                if url and value:
                    extension_map[url] = value

            # Handle extensions with direct value fields
            if 'valueString' in ext:
                extension_map[url] = ext['valueString']
            elif 'valueCode' in ext:
                extension_map[url] = ext['valueCode']
            elif 'valueAddress' in ext:
                extension_map[url] = ext['valueAddress']
            elif 'valueDecimal' in ext:
                extension_map[url] = ext['valueDecimal']
            elif 'valueCoding' in ext:
                extension_map[url] = ext['valueCoding']

        # Extract maritalStatus
        marital_status = resource.get('maritalStatus', {}).get('text')

        # Extract multipleBirthBoolean
        multiple_birth = resource.get('multipleBirthBoolean')

        # Extract communication languages
        communication = resource.get('communication', [])
        languages = [comm.get('language', {}).get('coding', [{}])[0].get('display') for comm in communication]

        # Extract telecom
        telecom = resource.get('telecom', [])

        # Extract gender
        gender = resource.get('gender')

        # Extract birthDate
        birth_date = resource.get('birthDate')

        # Extract address
        address = resource.get('address', [{}])[0]
        coordinates = f"({address.get('extension', [{}])[0].get('extension', [{}])[0].get('valueDecimal', '')}, {address.get('extension', [{}])[0].get('extension', [{}])[1].get('valueDecimal', '')})"
        full_address = f"{address.get('line', [''])[0]} {address.get('city', '')} {address.get('state', '')} {address.get('postalCode', '')} {address.get('country', '')}"

        metadata = {
            'id': patient_id,
            'full_name': full_name,
            'identifiers': identifier_map,
            'extensions': extension_map,
            'marital_status': marital_status,
            'multiple_birth': multiple_birth,
            'languages': languages,
            'telecom': telecom,
            'gender': gender,
            'birth_date': birth_date,
            'coordinates': coordinates,
            'full_address': full_address
        }
        return metadata

    def get_organization_metadata(self, resource):
        # Extract id
        organization_id = resource.get('id')
        # Extract name
        name = resource.get('name')


        # Extract identifiers
        identifiers = resource.get('identifier', [])
        identifier_map = {}
        for identifier in identifiers:
            system = identifier.get('system')
            value = identifier.get('value')
            if system and value:
                identifier_map[system] = value

        # Extract active status
        active = resource.get('active')

        # Extract type (display field under coding)
        types = resource.get('type', [])
        type_list = [t.get('coding', [{}])[0].get('display') for t in types]

        # Extract telecom
        telecom = resource.get('telecom', [])

        # Extract address
        address = resource.get('address', [{}])[0]
        full_address = f"{address.get('line', [''])[0]} {address.get('city', '')} {address.get('state', '')} {address.get('postalCode', '')} {address.get('country', '')}"

        metadata = {
            'id': organization_id,
            'name': name,
            'identifiers': identifier_map,
            'active': active,
            'type': type_list,
            'telecom': telecom,
            'full_address': full_address
        }
        return metadata

    def get_practitioner_metadata(self, resource):
        # Extract id
        practitioner_id = resource.get('id')

        # Extract name
        name = resource.get('name', [{}])[0]
        full_name = f"{name.get('prefix', [''])[0]} {name.get('given', [''])[0]} {name.get('family', '')}".strip()

        # Extract identifiers
        identifiers = resource.get('identifier', [])
        identifier_map = {}
        for identifier in identifiers:
            system = identifier.get('system')
            value = identifier.get('value')
            if system and value:
                identifier_map[system] = value

        # Extract active status
        active = resource.get('active')

        # Extract address
        address = resource.get('address', [{}])[0]
        full_address = f"{address.get('line', [''])[0]} {address.get('city', '')} {address.get('state', '')} {address.get('postalCode', '')} {address.get('country', '')}"

        metadata = {
            'practitioner_id': practitioner_id,
            'full_name': full_name,
            'identifiers': identifier_map,
            'active': active,
            'full_address': full_address
        }
        return metadata

    def get_encounter_metadata(self, resource):
        # Extract id
        encounter_id = resource.get('id')

        # Extract status
        status = resource.get('status')

        # Extract class
        encounter_class = resource.get('class', {}).get('code')

        # Extract type
        types = resource.get('type', [])
        type_list = [t.get('coding', [{}])[0].get('display') for t in types]

        # Extract subject
        subject = resource.get('subject', {}).get('reference', '')
        subject_id = subject.split(':')[-1] if 'urn:uuid:' in subject else subject

        # Extract participant
        participants = resource.get('participant', [])
        participant_list = [p.get('individual', {}).get('reference', '').split(':')[-1] if 'urn:uuid:' in p.get('individual', {}).get('reference', '') else p.get('individual', {}).get('reference', '') for p in participants]

        # Extract period
        period = resource.get('period', {})
        period_start = period.get('start')
        period_end = period.get('end')
        # period_key = f"{period_start} to {period_end}"

        # Extract serviceProvider
        service_provider = resource.get('serviceProvider', {}).get('reference', '')
        service_provider_id = service_provider.split(':')[-1] if 'urn:uuid:' in service_provider else service_provider

        metadata = {
            'encounter_id': encounter_id,
            'status': status,
            'class': encounter_class,
            'type': type_list,
            'subject': subject_id,
            'participants': participant_list,
            'period_start': period_start,
            'period_end': period_end,
            'service_provider': service_provider_id
        }
        return metadata

    def get_condition_metadata(self, resource):
        # Extract id
        condition_id = resource.get('id')

        # Extract clinical status
        clinical_status = resource.get('clinicalStatus', {}).get('coding', [{}])[0].get('code')

        # Extract verification status
        verification_status = resource.get('verificationStatus', {}).get('coding', [{}])[0].get('code')

        # Extract code
        code = resource.get('code', {}).get('coding', [{}])[0].get('display')

        # Extract subject
        subject = resource.get('subject', {}).get('reference', '')
        subject_id = subject.split(':')[-1] if 'urn:uuid:' in subject else subject

        # Extract encounter
        encounter = resource.get('encounter', {}).get('reference', '')
        encounter_id = encounter.split(':')[-1] if 'urn:uuid:' in encounter else encounter

        # Extract onsetDateTime
        onset_date_time = resource.get('onsetDateTime')

        # Extract recordedDate
        recorded_date = resource.get('recordedDate')

        metadata = {
            'condition_id': condition_id,
            'clinical_status': clinical_status,
            'verification_status': verification_status,
            'code': code,
            'subject': subject_id,
            'encounter': encounter_id,
            'onset_datetime': onset_date_time,
            'recorded_date': recorded_date
        }
        return metadata

    def get_observation_metadata(self, resource):
        # Extract id
        observation_id = resource.get('id')

        # Extract status
        status = resource.get('status')

        # Extract category
        category = resource.get('category', [{}])[0].get('coding', [{}])[0].get('display')

        # Extract code
        code = resource.get('code', {}).get('coding', [{}])[0].get('display')

        # Extract subject
        subject = resource.get('subject', {}).get('reference', '')
        subject_id = subject.split(':')[-1] if 'urn:uuid:' in subject else subject

        # Extract encounter
        encounter = resource.get('encounter', {}).get('reference', '')
        encounter_id = encounter.split(':')[-1] if 'urn:uuid:' in encounter else encounter

        # Extract effectiveDateTime
        effective_date_time = resource.get('effectiveDateTime')

        # Extract issued
        issued = resource.get('issued')

        # Extract valueQuantity
        value_quantity = resource.get('valueQuantity', {})
        value = value_quantity.get('value')
        unit = value_quantity.get('unit')

        metadata = {
            'Observation ID': observation_id,
            'Status': status,
            'Category': category,
            'Code': code,
            'Subject': subject_id,
            'Encounter': encounter_id,
            'Effective DateTime': effective_date_time,
            'Issued': issued,
            'Value': value,
            'Unit': unit
        }
        return metadata   
        
    def get_immunization_metadata(self, resource):
        # Extract id
        immunization_id = resource.get('id')

        # Extract status
        status = resource.get('status')

        # Extract vaccine code
        vaccine_code = resource.get('vaccineCode', {}).get('coding', [{}])[0].get('display')

        # Extract patient
        patient = resource.get('patient', {}).get('reference', '')
        patient_id = patient.split(':')[-1] if 'urn:uuid:' in patient else patient

        # Extract encounter
        encounter = resource.get('encounter', {}).get('reference', '')
        encounter_id = encounter.split(':')[-1] if 'urn:uuid:' in encounter else encounter

        # Extract occurrence date/time
        occurrence_date_time = resource.get('occurrenceDateTime')

        # Extract primary source
        primary_source = resource.get('primarySource')

        metadata = {
            'Immunization ID': immunization_id,
            'Status': status,
            'Vaccine Code': vaccine_code,
            'Patient': patient_id,
            'Encounter': encounter_id,
            'Occurrence DateTime': occurrence_date_time,
            'Primary Source': primary_source
        }
        return metadata

    def get_diagnostic_report_metadata(self, resource):
        # Extract id
        diagnostic_report_id = resource.get('id')

        # Extract status
        status = resource.get('status')

        # Extract category
        category = resource.get('category', [{}])[0].get('coding', [{}])[0].get('display')

        # Extract code
        code = resource.get('code', {}).get('coding', [{}])[0].get('display')

        # Extract subject
        subject = resource.get('subject', {}).get('reference', '')
        subject_id = subject.split(':')[-1] if 'urn:uuid:' in subject else subject

        # Extract encounter
        encounter = resource.get('encounter', {}).get('reference', '')
        encounter_id = encounter.split(':')[-1] if 'urn:uuid:' in encounter else encounter

        # Extract effectiveDateTime
        effective_date_time = resource.get('effectiveDateTime')

        # Extract issued
        issued = resource.get('issued')

        # Extract result
        results = resource.get('result', [])
        result_list = [r.get('display') for r in results]

        metadata = {
            'Diagnostic Report ID': diagnostic_report_id,
            'Status': status,
            'Category': category,
            'Code': code,
            'Subject': subject_id,
            'Encounter': encounter_id,
            'Effective DateTime': effective_date_time,
            'Issued': issued,
            'Result': result_list
        }
        return metadata

    def get_procedure_metadata(self, resource):
        # Extract id
        procedure_id = resource.get('id')

        # Extract status
        status = resource.get('status')

        # Extract code
        code = resource.get('code', {}).get('coding', [{}])[0].get('display')

        # Extract subject
        subject = resource.get('subject', {}).get('reference', '')
        subject_id = subject.split(':')[-1] if 'urn:uuid:' in subject else subject

        # Extract encounter
        encounter = resource.get('encounter', {}).get('reference', '')
        encounter_id = encounter.split(':')[-1] if 'urn:uuid:' in encounter else encounter

        # Extract performedPeriod
        performed_period = resource.get('performedPeriod', {})
        performed_start = performed_period.get('start')
        performed_end = performed_period.get('end')

        # Extract performer
        performers = resource.get('performer', [])
        performer_list = [p.get('actor', {}).get('reference', '').split(':')[-1] if 'urn:uuid:' in p.get('actor', {}).get('reference', '') else p.get('actor', {}).get('reference', '') for p in performers]

        metadata = {
            'Procedure ID': procedure_id,
            'Status': status,
            'Code': code,
            'Subject': subject_id,
            'Encounter': encounter_id,
            'Performed Start': performed_start,
            'Performed End': performed_end
        }
        return metadata

    def get_medication_request_metadata(self, resource):
        # Extract id
        medication_request_id = resource.get('id')

        # Extract status
        status = resource.get('status')

        # Extract intent
        intent = resource.get('intent')

        # Extract medication code
        medication_code = resource.get('medicationCodeableConcept', {}).get('coding', [{}])[0].get('display')

        # Extract subject
        subject = resource.get('subject', {}).get('reference', '')
        subject_id = subject.split(':')[-1] if 'urn:uuid:' in subject else subject

        # Extract encounter
        encounter = resource.get('encounter', {}).get('reference', '')
        encounter_id = encounter.split(':')[-1] if 'urn:uuid:' in encounter else encounter

        # Extract authoredOn
        authored_on = resource.get('authoredOn')

        # Extract requester
        requester = resource.get('requester', {}).get('reference', '')
        requester_id = requester.split(':')[-1] if 'urn:uuid:' in requester else requester

        metadata = {
            'Medication Request ID': medication_request_id,
            'Status': status,
            'Intent': intent,
            'Medication Code': medication_code,
            'Subject': subject_id,
            'Encounter': encounter_id,
            'Authored On': authored_on,
            'Requester': requester_id
        }
        return metadata

    def get_entities(self):
        entity_map = {
            'Patient': 1, 'Organization': 1, 'Practitioner': 1, 'Encounter': 16, 'Condition': 3,
            'Claim': 18, 'ExplanationOfBenefit': 16, 'Observation': 94, 'Immunization': 11,
            'DiagnosticReport': 5, 'Procedure': 10, 'MedicationRequest': 2, 'CarePlan': 1, 'ImagingStudy': 1
        }
        result = {}
        
        for entry in self.json_data['entry']:
            resource = entry['resource']
            resource_type = resource['resourceType']
            if resource_type in entity_map:
                if entity_map[resource_type] > 1:
                    if resource_type not in result:
                        result[resource_type] = []
                    if resource_type == 'Encounter':
                        result[resource_type].append({'resource': resource, 'metadata': self.get_encounter_metadata(resource)})
                    elif resource_type == 'Condition':
                        result[resource_type].append({'resource': resource, 'metadata': self.get_condition_metadata(resource)})
                    elif resource_type == 'Observation':
                        result[resource_type].append({'resource': resource, 'metadata': self.get_observation_metadata(resource)})
                    elif resource_type == 'Immunization':
                        result[resource_type].append({'resource': resource, 'metadata': self.get_immunization_metadata(resource)})
                    elif resource_type == 'DiagnosticReport':
                        result[resource_type].append({'resource': resource, 'metadata': self.get_diagnostic_report_metadata(resource)})
                    elif resource_type == 'Procedure':
                        result[resource_type].append({'resource': resource, 'metadata': self.get_procedure_metadata(resource)})
                    elif resource_type == 'MedicationRequest':
                        result[resource_type].append({'resource': resource, 'metadata': self.get_medication_request_metadata(resource)})
                    else:
                        result[resource_type].append({'resource': resource, 'metadata': f'{resource_type} metadata'})
                else:
                    if resource_type == 'Patient':
                        result[resource_type] = {'resource': resource, 'metadata': self.get_patient_metadata(resource)}
                    elif resource_type == 'Organization':
                        result[resource_type] = {'resource': resource, 'metadata': self.get_organization_metadata(resource)}
                    elif resource_type == 'Practitioner':
                        result[resource_type] = {'resource': resource, 'metadata': self.get_practitioner_metadata(resource)}
                    else:
                        result[resource_type] = resource
        
        return result

    def pretty_print_metadata(self, resourceType):
        retriever = self.json_data
        entities = self.get_entities()
        if resourceType == 'Encounter':
            metadata = [encounter['metadata'] for encounter in entities.get(resourceType, [])]
        elif resourceType == 'Condition':
            metadata = [condition['metadata'] for condition in entities.get(resourceType, [])]
        elif resourceType == 'Observation':
            metadata = [observation['metadata'] for observation in entities.get(resourceType, [])]
        elif resourceType == 'Immunization':
            metadata = [immunization['metadata'] for immunization in entities.get(resourceType, [])]
        elif resourceType == 'DiagnosticReport':
            metadata = [diagnostic_report['metadata'] for diagnostic_report in entities.get(resourceType, [])]
        elif resourceType == 'Procedure':
            metadata = [procedure['metadata'] for procedure in entities.get(resourceType, [])]
        elif resourceType == 'MedicationRequest':
            metadata = [medication_request['metadata'] for medication_request in entities.get(resourceType, [])]
        else:
            metadata = entities.get(resourceType, {}).get('metadata', {})
        
        print(json.dumps(metadata, indent=4))

    def patient_projection(entities):
        patient_dict = entities.get("Patient", {}).get('metadata', {})

        # Keys to project
        keys_to_project = ['full_name', 'marital_status', 'languages', 'gender']
        projected_dict = {key: patient_dict[key] for key in keys_to_project}

        # 
        projected_dict['age'] = EntityRetriever.calculate_age(patient_dict['birth_date'])
        return projected_dict

    def practitioner_projection(entities):
        practitioner_dict = entities.get("Practitioner", {}).get('metadata', {})

        # Keys to project
        keys_to_project = ['practitioner_id']
        projected_dict = {key: practitioner_dict[key] for key in keys_to_project}

        return projected_dict

    def conditions_projection(entities):
        projected_dict = dict()
        projected_dict['conditions'] = [condition['metadata']['code'] for condition in entities.get("Condition", [])]
        return projected_dict

    def encounter_projection(encounter):
        # Add more like Encounter transcript, Suggested {interventions, questions, tests, medications}, Followup, Generated Summary, subjective Summary, objective summary, assessment, clinical plan 
        # icd 10 codes, cpt codes
        # Keys to project
        keys_to_project = ['encounter_id', 'status', 'class', 'type', 'period_start', 'period_end']
        return {key: encounter['metadata'][key] for key in keys_to_project}



def printParsedDataFromFile():

    # Example usage
    with open('/Users/pranayhasan/workspace/generated-sample-data/R4/SYNTHEA/Abdul_Koepp_e925b0f3-8006-43f6-aa31-94bd215e55e7.json', 'r') as file:
        data = json.load(file)

    obj = EntityRetriever(data)

    print('\n\n\n')
    print('Patient')
    obj.pretty_print_metadata("Patient")
    print('\n\n\n')
    print('Organization')
    obj.pretty_print_metadata("Organization")
    print('\n\n\n')
    print('Practitioner')
    obj.pretty_print_metadata("Practitioner")
    print('\n\n\n')
    print('Encounter')
    obj.pretty_print_metadata("Encounter")
    print('\n\n\n')
    print('Condition')
    obj.pretty_print_metadata("Condition")
    print('\n\n\n')
    print('Observation')
    obj.pretty_print_metadata("Observation")
    print('\n\n\n')
    print('Immunization')
    obj.pretty_print_metadata("Immunization")
    print('\n\n\n')
    print('DiagnosticReport')
    obj.pretty_print_metadata("DiagnosticReport")
    print('\n\n\n')
    print('Procedure')
    obj.pretty_print_metadata("Procedure")
    print('\n\n\n')
    print('MedicationRequest')
    obj.pretty_print_metadata("MedicationRequest")


class TypesenseClient:
    def __init__(self, host='localhost', port='8108', protocol='http', api_key='xyz', index_name='encounters', path='/Users/pranayhasan/workspace/generated-sample-data/R4/SYNTHEA/'):
        self.client = typesense.Client({
            'nodes': [{
                'host': host,
                'port': port,
                'protocol': protocol
            }],
            'api_key': api_key,
            'connection_timeout_seconds': 2
        })
        self.index_name = index_name
        self.path = path
        self.schema = {
            'name': self.index_name,
            'enable_nested_fields': True,
            'fields': [
                # {'name': 'patient', 'type': 'object'},
                # {'name': 'patient.ethnicity', 'type': 'string', 'stem': True},
                # {'name': 'birthsex', 'type': 'string'},
                # {'name': 'birthplace', 'type': 'string'},
                # {'name': 'marital_status', 'type': 'string'},
                # {'name': 'multiple_birth', 'type': 'bool'},
                {'name': 'practitioner_id', 'type': 'string'},
                {'name': 'conditions', 'type': 'string[]'},
                {'name': 'encounter_id', 'type': 'string'},
                {'name': 'status', 'type': 'string', 'facet': True},
                {'name': 'class', 'type': 'string', 'index': False},
                {'name': 'type', 'type': 'string[]'},
                {'name': 'period_start', 'type': 'string', 'facet': True, 'sort': True},
                {'name': 'period_end', 'type': 'string', 'facet': True},
                {'name': 'full_name', 'type': 'string'},
                {'name': 'marital_status', 'type': 'string', 'facet': True},
                {'name': 'languages', 'type': 'string[]', 'facet': True},
                {'name': 'gender', 'type': 'string', 'facet': True},
                {'name': 'age', 'type': 'int32', 'facet': True, 'range_index': True},
                {'name': 'embedding', 'type': 'float[]', 'embed': {'from': ['full_name', 'languages', 'conditions'], 'model_config': { 'model_name': 'ts/all-MiniLM-L12-v2'}}}
            ],
            'default_sorting_field': 'period_start'
        }

    def refresh_collection(self):
        try:
            self.client.collections[self.index_name].delete()
            print(f"Deleted existing collection: {self.index_name}")
        except typesense.exceptions.ObjectNotFound:
            print(f"No collection named {self.index_name} found to delete.")
        
        self.client.collections.create(self.schema)
        print(f"Created collection with schema: {self.index_name}")

    def index_documents(self):
        self.refresh_collection()

        cnt = 0
        encounterCnt = 0
        for filename in os.listdir(self.path):
            file_path = os.path.join(self.path, filename)
            if os.path.isfile(file_path) and not file_path.startswith(('hospitalInformation', 'practitionerInformation', '.')):
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    retriever = EntityRetriever(data)
                    entities = retriever.get_entities()

                    cnt += 1
                    encounterCnt += len(entities.get('Encounter', []))
                    print(f"{(cnt/631) * 100 :.0f}% INDEXING PATIENT FILE: {file_path} - {len(entities.get('Encounter', []))} encounters")

                    for encounter in entities.get("Encounter", []):
                        document = {}
                        document.update(EntityRetriever.patient_projection(entities)) # patient fields
                        document.update(EntityRetriever.practitioner_projection(entities)) # practitioner fields
                        document.update(EntityRetriever.conditions_projection(entities)) # condition fields
                        document.update(EntityRetriever.encounter_projection(encounter))

                        self.client.collections[self.index_name].documents.create(document)
                        # print(f"Indexed document: {document}")

        print(f"Total Encounters: {encounterCnt}")

    def hybrid_search(self, practitioner_id, query, age_range=(0, 124)):
        vector_results_limit=200 # limits the no of results from vector search

        search_parameters = {
            'q': query,
            'query_by': 'full_name,languages,period_start,conditions,embedding',
            'query_by_weights': '3,1,1,1,0',
            'text_match_type': 'sum_score', # max_score (default), max_weight, sum_score
            'filter_by': f'practitioner_id:={practitioner_id} && age:[<{age_range[1]}, >{age_range[0]}]', # && marital_status:=[M,S,Never Married] 
            'sort_by': '_text_match:desc,period_start:desc', #_text_match:desc or period_start:desc
            'vector_query': f'embedding:([], k: {vector_results_limit})',
            'exclude_fields': 'embedding',
            'per_page': 5,
            'page': 1
        }

        result = self.client.collections[self.index_name].documents.search(search_parameters)
        formatted_json = json.dumps(result, indent=2)
        print(formatted_json)


# Example usage
if __name__ == "__main__":
    # Initialize the TypesenseClient
    client = TypesenseClient()

    # Index documents
    # client.index_documents()

    # Perform a search
    client.hybrid_search('6d705d81-8546-43b2-b336-31a282128f2d', query="Koepp", age_range=(1, 90)) 

# printParsedDataFromFile()

