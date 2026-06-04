# Primavera P6 Integration Module
# Bi-directional sync between Omnexa Construction and Primavera P6

import frappe
from frappe import _
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class PrimaveraP6Client:
    """Client for Primavera P6 REST API"""
    
    def __init__(self, base_url: str, username: str, password: str, company_id: str):
        """
        Initialize P6 Client
        
        Args:
            base_url: P6 REST API base URL (e.g., https://p6-server/p6ws/rest/api)
            username: P6 username
            password: P6 password
            company_id: P6 company ID
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.company_id = company_id
        self.session = requests.Session()
        self.auth_token = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with P6 server"""
        try:
            auth_url = f"{self.base_url}/auth/login"
            payload = {
                "username": self.username,
                "password": self.password,
                "companyId": self.company_id
            }
            
            response = self.session.post(auth_url, json=payload, timeout=30)
            response.raise_for_status()
            
            self.auth_token = response.json().get('token')
            self.session.headers.update({
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json'
            })
            
            logger.info("Successfully authenticated with Primavera P6")
            
        except Exception as e:
            logger.error(f"P6 Authentication failed: {str(e)}")
            frappe.throw(_("Failed to authenticate with Primavera P6: {0}").format(str(e)))
    
    def get_projects(self) -> List[Dict]:
        """Get all projects from P6"""
        try:
            url = f"{self.base_url}/project"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json().get('projects', [])
        except Exception as e:
            logger.error(f"Failed to get projects from P6: {str(e)}")
            return []
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get specific project from P6"""
        try:
            url = f"{self.base_url}/project/{project_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get project {project_id} from P6: {str(e)}")
            return None
    
    def create_project(self, project_data: Dict) -> Optional[str]:
        """Create project in P6"""
        try:
            url = f"{self.base_url}/project"
            response = self.session.post(url, json=project_data, timeout=30)
            response.raise_for_status()
            return response.json().get('projectId')
        except Exception as e:
            logger.error(f"Failed to create project in P6: {str(e)}")
            return None
    
    def update_project(self, project_id: str, project_data: Dict) -> bool:
        """Update project in P6"""
        try:
            url = f"{self.base_url}/project/{project_id}"
            response = self.session.put(url, json=project_data, timeout=30)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to update project {project_id} in P6: {str(e)}")
            return False
    
    def get_activities(self, project_id: str) -> List[Dict]:
        """Get all activities for a project from P6"""
        try:
            url = f"{self.base_url}/project/{project_id}/activity"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json().get('activities', [])
        except Exception as e:
            logger.error(f"Failed to get activities for project {project_id} from P6: {str(e)}")
            return []
    
    def create_activity(self, project_id: str, activity_data: Dict) -> Optional[str]:
        """Create activity in P6"""
        try:
            url = f"{self.base_url}/project/{project_id}/activity"
            response = self.session.post(url, json=activity_data, timeout=30)
            response.raise_for_status()
            return response.json().get('activityId')
        except Exception as e:
            logger.error(f"Failed to create activity in P6: {str(e)}")
            return None
    
    def update_activity(self, project_id: str, activity_id: str, activity_data: Dict) -> bool:
        """Update activity in P6"""
        try:
            url = f"{self.base_url}/project/{project_id}/activity/{activity_id}"
            response = self.session.put(url, json=activity_data, timeout=30)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to update activity {activity_id} in P6: {str(e)}")
            return False
    
    def get_resources(self) -> List[Dict]:
        """Get all resources from P6"""
        try:
            url = f"{self.base_url}/resource"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json().get('resources', [])
        except Exception as e:
            logger.error(f"Failed to get resources from P6: {str(e)}")
            return []
    
    def create_resource(self, resource_data: Dict) -> Optional[str]:
        """Create resource in P6"""
        try:
            url = f"{self.base_url}/resource"
            response = self.session.post(url, json=resource_data, timeout=30)
            response.raise_for_status()
            return response.json().get('resourceId')
        except Exception as e:
            logger.error(f"Failed to create resource in P6: {str(e)}")
            return None
    
    def update_resource(self, resource_id: str, resource_data: Dict) -> bool:
        """Update resource in P6"""
        try:
            url = f"{self.base_url}/resource/{resource_id}"
            response = self.session.put(url, json=resource_data, timeout=30)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to update resource {resource_id} in P6: {str(e)}")
            return False
    
    def get_baselines(self, project_id: str) -> List[Dict]:
        """Get baselines for a project from P6"""
        try:
            url = f"{self.base_url}/project/{project_id}/baseline"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json().get('baselines', [])
        except Exception as e:
            logger.error(f"Failed to get baselines for project {project_id} from P6: {str(e)}")
            return []
    
    def create_baseline(self, project_id: str, baseline_data: Dict) -> Optional[str]:
        """Create baseline in P6"""
        try:
            url = f"{self.base_url}/project/{project_id}/baseline"
            response = self.session.post(url, json=baseline_data, timeout=30)
            response.raise_for_status()
            return response.json().get('baselineId')
        except Exception as e:
            logger.error(f"Failed to create baseline in P6: {str(e)}")
            return None


class PrimaveraP6Mapper:
    """Mapper between Omnexa and P6 data structures"""
    
    @staticmethod
    def map_omnexa_project_to_p6(project_doc: Dict) -> Dict:
        """Map Omnexa Project Contract to P6 Project"""
        return {
            "name": project_doc.get('project_name'),
            "code": project_doc.get('name'),
            "description": project_doc.get('description', ''),
            "startDate": project_doc.get('start_date'),
            "finishDate": project_doc.get('end_date'),
            "calendarId": project_doc.get('p6_calendar_id', 'Default'),
            "status": project_doc.get('status', 'Active'),
            "customFields": {
                "omnexa_project_id": project_doc.get('name'),
                "contract_value": project_doc.get('contract_value'),
                "contract_type": project_doc.get('contract_type')
            }
        }
    
    @staticmethod
    def map_p6_project_to_omnexa(p6_project: Dict) -> Dict:
        """Map P6 Project to Omnexa Project Contract"""
        return {
            "project_name": p6_project.get('name'),
            "name": p6_project.get('code'),
            "description": p6_project.get('description', ''),
            "start_date": p6_project.get('startDate'),
            "end_date": p6_project.get('finishDate'),
            "status": p6_project.get('status', 'Active'),
            "p6_project_id": p6_project.get('projectId'),
            "p6_project_object_id": p6_project.get('objectId')
        }
    
    @staticmethod
    def map_omnexa_task_to_p6(task_doc: Dict) -> Dict:
        """Map Omnexa PM WBS Task to P6 Activity"""
        return {
            "name": task_doc.get('subject'),
            "code": task_doc.get('name'),
            "description": task_doc.get('description', ''),
            "startDate": task_doc.get('exp_start_date'),
            "finishDate": task_doc.get('exp_end_date'),
            "duration": task_doc.get('duration', 0),
            "durationType": task_doc.get('duration_type', 'FixedDuration'),
            "activityType": task_doc.get('activity_type', 'TaskActivity'),
            "status": task_doc.get('status', 'NotStarted'),
            "customFields": {
                "omnexa_task_id": task_doc.get('name'),
                "wbs_id": task_doc.get('wbs_id'),
                "boq_item": task_doc.get('boq_item')
            }
        }
    
    @staticmethod
    def map_p6_activity_to_omnexa(p6_activity: Dict) -> Dict:
        """Map P6 Activity to Omnexa PM WBS Task"""
        return {
            "subject": p6_activity.get('name'),
            "name": p6_activity.get('code'),
            "description": p6_activity.get('description', ''),
            "exp_start_date": p6_activity.get('startDate'),
            "exp_end_date": p6_activity.get('finishDate'),
            "duration": p6_activity.get('duration', 0),
            "status": p6_activity.get('status', 'NotStarted'),
            "p6_activity_id": p6_activity.get('activityId'),
            "p6_activity_object_id": p6_activity.get('objectId')
        }
    
    @staticmethod
    def map_omnexa_resource_to_p6(resource_doc: Dict) -> Dict:
        """Map Omnexa Resource to P6 Resource"""
        return {
            "name": resource_doc.get('resource_name'),
            "code": resource_doc.get('name'),
            "description": resource_doc.get('description', ''),
            "resourceType": resource_doc.get('resource_type', 'Labor'),
            "unitOfMeasure": resource_doc.get('uom', 'Hours'),
            "customFields": {
                "omnexa_resource_id": resource_doc.get('name'),
                "cost_per_unit": resource_doc.get('cost_per_hour')
            }
        }
    
    @staticmethod
    def map_p6_resource_to_omnexa(p6_resource: Dict) -> Dict:
        """Map P6 Resource to Omnexa Resource"""
        return {
            "resource_name": p6_resource.get('name'),
            "name": p6_resource.get('code'),
            "description": p6_resource.get('description', ''),
            "resource_type": p6_resource.get('resourceType', 'Labor'),
            "uom": p6_resource.get('unitOfMeasure', 'Hours'),
            "p6_resource_id": p6_resource.get('resourceId'),
            "p6_resource_object_id": p6_resource.get('objectId')
        }


class PrimaveraP6Sync:
    """Sync manager for bi-directional sync"""
    
    def __init__(self, p6_client: PrimaveraP6Client):
        self.p6_client = p6_client
        self.mapper = PrimaveraP6Mapper()
    
    def sync_project_to_p6(self, omnexa_project_id: str) -> Dict:
        """Sync Omnexa project to P6"""
        try:
            # Get Omnexa project
            project_doc = frappe.get_doc('Project Contract', omnexa_project_id)
            
            # Check if already synced
            p6_project_id = project_doc.get('p6_project_id')
            if p6_project_id:
                # Update existing
                p6_data = self.mapper.map_omnexa_project_to_p6(project_doc.as_dict())
                success = self.p6_client.update_project(p6_project_id, p6_data)
                if success:
                    self._update_sync_status(project_doc, 'Synced')
                    self._log_sync('project', omnexa_project_id, 'update', 'success')
                    return {'status': 'success', 'action': 'updated'}
                else:
                    self._update_sync_status(project_doc, 'Sync Failed')
                    self._log_sync('project', omnexa_project_id, 'update', 'failed')
                    return {'status': 'failed', 'action': 'update'}
            else:
                # Create new
                p6_data = self.mapper.map_omnexa_project_to_p6(project_doc.as_dict())
                new_p6_project_id = self.p6_client.create_project(p6_data)
                
                if new_p6_project_id:
                    # Update Omnexa project with P6 ID
                    project_doc.p6_project_id = new_p6_project_id
                    self._update_sync_status(project_doc, 'Synced')
                    project_doc.save()
                    self._log_sync('project', omnexa_project_id, 'create', 'success')
                    return {'status': 'success', 'action': 'created', 'p6_project_id': new_p6_project_id}
                else:
                    self._update_sync_status(project_doc, 'Sync Failed')
                    self._log_sync('project', omnexa_project_id, 'create', 'failed')
                    return {'status': 'failed', 'action': 'create'}
                    
        except Exception as e:
            logger.error(f"Failed to sync project {omnexa_project_id} to P6: {str(e)}")
            self._log_sync('project', omnexa_project_id, 'sync', 'failed', str(e))
            return {'status': 'failed', 'error': str(e)}
    
    def sync_project_from_p6(self, p6_project_id: str) -> Dict:
        """Sync P6 project to Omnexa"""
        try:
            # Get P6 project
            p6_project = self.p6_client.get_project(p6_project_id)
            if not p6_project:
                return {'status': 'failed', 'error': 'Project not found in P6'}
            
            # Check if already exists in Omnexa
            existing_project = frappe.db.exists('Project Contract', {'p6_project_id': p6_project_id})
            
            if existing_project:
                # Update existing
                omnexa_data = self.mapper.map_p6_project_to_omnexa(p6_project)
                project_doc = frappe.get_doc('Project Contract', existing_project)
                project_doc.update(omnexa_data)
                project_doc.save()
                self._log_sync('project', existing_project, 'update_from_p6', 'success')
                return {'status': 'success', 'action': 'updated', 'omnexa_project_id': existing_project}
            else:
                # Create new
                omnexa_data = self.mapper.map_p6_project_to_omnexa(p6_project)
                project_doc = frappe.new_doc('Project Contract')
                project_doc.update(omnexa_data)
                project_doc.insert()
                self._log_sync('project', project_doc.name, 'create_from_p6', 'success')
                return {'status': 'success', 'action': 'created', 'omnexa_project_id': project_doc.name}
                
        except Exception as e:
            logger.error(f"Failed to sync project {p6_project_id} from P6: {str(e)}")
            self._log_sync('project', p6_project_id, 'sync_from_p6', 'failed', str(e))
            return {'status': 'failed', 'error': str(e)}
    
    def sync_task_to_p6(self, omnexa_task_id: str) -> Dict:
        """Sync Omnexa task to P6"""
        try:
            # Get Omnexa task
            task_doc = frappe.get_doc('PM WBS Task', omnexa_task_id)
            
            # Get project P6 ID
            project_doc = frappe.get_doc('Project Contract', task_doc.project)
            if not project_doc.get('p6_project_id'):
                return {'status': 'failed', 'error': 'Project not synced to P6'}
            
            # Check if already synced
            p6_activity_id = task_doc.get('p6_activity_id')
            if p6_activity_id:
                # Update existing
                p6_data = self.mapper.map_omnexa_task_to_p6(task_doc.as_dict())
                success = self.p6_client.update_activity(
                    project_doc.get('p6_project_id'),
                    p6_activity_id,
                    p6_data
                )
                if success:
                    self._update_sync_status(task_doc, 'Synced')
                    self._log_sync('task', omnexa_task_id, 'update', 'success')
                    return {'status': 'success', 'action': 'updated'}
                else:
                    self._update_sync_status(task_doc, 'Sync Failed')
                    self._log_sync('task', omnexa_task_id, 'update', 'failed')
                    return {'status': 'failed', 'action': 'update'}
            else:
                # Create new
                p6_data = self.mapper.map_omnexa_task_to_p6(task_doc.as_dict())
                new_p6_activity_id = self.p6_client.create_activity(
                    project_doc.get('p6_project_id'),
                    p6_data
                )
                
                if new_p6_activity_id:
                    # Update Omnexa task with P6 ID
                    task_doc.p6_activity_id = new_p6_activity_id
                    self._update_sync_status(task_doc, 'Synced')
                    task_doc.save()
                    self._log_sync('task', omnexa_task_id, 'create', 'success')
                    return {'status': 'success', 'action': 'created', 'p6_activity_id': new_p6_activity_id}
                else:
                    self._update_sync_status(task_doc, 'Sync Failed')
                    self._log_sync('task', omnexa_task_id, 'create', 'failed')
                    return {'status': 'failed', 'action': 'create'}
                    
        except Exception as e:
            logger.error(f"Failed to sync task {omnexa_task_id} to P6: {str(e)}")
            self._log_sync('task', omnexa_task_id, 'sync', 'failed', str(e))
            return {'status': 'failed', 'error': str(e)}
    
    def sync_resource_to_p6(self, omnexa_resource_id: str) -> Dict:
        """Sync Omnexa resource to P6"""
        try:
            # Get Omnexa resource
            resource_doc = frappe.get_doc('Resource', omnexa_resource_id)
            
            # Check if already synced
            p6_resource_id = resource_doc.get('p6_resource_id')
            if p6_resource_id:
                # Update existing
                p6_data = self.mapper.map_omnexa_resource_to_p6(resource_doc.as_dict())
                success = self.p6_client.update_resource(p6_resource_id, p6_data)
                if success:
                    self._update_sync_status(resource_doc, 'Synced')
                    self._log_sync('resource', omnexa_resource_id, 'update', 'success')
                    return {'status': 'success', 'action': 'updated'}
                else:
                    self._update_sync_status(resource_doc, 'Sync Failed')
                    self._log_sync('resource', omnexa_resource_id, 'update', 'failed')
                    return {'status': 'failed', 'action': 'update'}
            else:
                # Create new
                p6_data = self.mapper.map_omnexa_resource_to_p6(resource_doc.as_dict())
                new_p6_resource_id = self.p6_client.create_resource(p6_data)
                
                if new_p6_resource_id:
                    # Update Omnexa resource with P6 ID
                    resource_doc.p6_resource_id = new_p6_resource_id
                    self._update_sync_status(resource_doc, 'Synced')
                    resource_doc.save()
                    self._log_sync('resource', omnexa_resource_id, 'create', 'success')
                    return {'status': 'success', 'action': 'created', 'p6_resource_id': new_p6_resource_id}
                else:
                    self._update_sync_status(resource_doc, 'Sync Failed')
                    self._log_sync('resource', omnexa_resource_id, 'create', 'failed')
                    return {'status': 'failed', 'action': 'create'}
                    
        except Exception as e:
            logger.error(f"Failed to sync resource {omnexa_resource_id} to P6: {str(e)}")
            self._log_sync('resource', omnexa_resource_id, 'sync', 'failed', str(e))
            return {'status': 'failed', 'error': str(e)}
    
    def _log_sync(self, entity_type: str, entity_id: str, action: str, status: str, error_message: str = None):
        """Log sync operation"""
        try:
            log_doc = frappe.new_doc('Primavera Integration Log')
            log_doc.entity_type = entity_type
            log_doc.entity_id = entity_id
            log_doc.action = action
            log_doc.status = status
            log_doc.error_message = error_message
            log_doc.sync_timestamp = datetime.now()
            log_doc.insert()
        except Exception as e:
            logger.error(f"Failed to log sync: {str(e)}")
    
    def _update_sync_status(self, doc, status: str):
        """Update sync status on document"""
        try:
            if doc.doctype == 'Project Contract':
                doc.p6_sync_status = status
                doc.p6_last_sync = datetime.now()
            elif doc.doctype == 'PM WBS Task':
                doc.p6_sync_status = status
                doc.p6_last_sync = datetime.now()
            elif doc.doctype == 'Resource':
                doc.p6_sync_status = status
                doc.p6_last_sync = datetime.now()
            doc.save()
        except Exception as e:
            logger.error(f"Failed to update sync status: {str(e)}")


def get_p6_client() -> PrimaveraP6Client:
    """Get configured P6 client"""
    settings = frappe.get_single('Primavera P6 Settings')
    
    if not settings.enabled:
        frappe.throw(_("Primavera P6 integration is not enabled"))
    
    if not all([settings.base_url, settings.username, settings.password, settings.company_id]):
        frappe.throw(_("Primavera P6 settings are incomplete"))
    
    return PrimaveraP6Client(
        base_url=settings.base_url,
        username=settings.username,
        password=settings.get_password('password'),
        company_id=settings.company_id
    )
